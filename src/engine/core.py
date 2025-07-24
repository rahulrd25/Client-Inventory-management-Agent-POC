
import pandas as pd
import os
import shutil

def clear_output_directory(output_path):
    """
    Clears all files from the specified output directory.
    """
    if os.path.exists(output_path):
        for filename in os.listdir(output_path):
            file_path = os.path.join(output_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        os.makedirs(output_path, exist_ok=True)


# Define a configurable threshold for excess stock in days of supply
EXCESS_DOS_THRESHOLD = 70 # As per new requirement

def run_replenishment_engine(
    branch_inventory_df=None,
    warehouse_stock_df=None,
    sku_master_df=None,
    data_path="data",
    output_path="outputs"
):
    """
    Runs the core replenishment logic based on a hub-and-spoke model.
    This includes calculating reorders, allocating stock, creating LPOs,
    and identifying excess stock based on Days of Stock (DOS).

    Args:
        branch_inventory_df (pd.DataFrame, optional): DataFrame for branch inventory.
        warehouse_stock_df (pd.DataFrame, optional): DataFrame for warehouse stock.
        sku_master_df (pd.DataFrame, optional): DataFrame for SKU master data.
        data_path (str): The path to the directory containing the input CSV data files (used if DataFrames are not provided).
        output_path (str): The path to the directory where output CSV files will be saved.

    Returns:
        tuple: A tuple containing four DataFrames:
               - merged_data: The merged and processed data with all calculations.
               - transfer_orders_df: The list of SKUs to be transferred from the warehouse.
               - lpo_needs_df: The list of SKUs that require a Local Purchase Order.
               - excess_stock_df: The list of SKUs that are overstocked at branches.
    """
    # --- 1. Load Data ---
    if branch_inventory_df is not None and warehouse_stock_df is not None and sku_master_df is not None:
        branch_inventory = branch_inventory_df
        warehouse_stock = warehouse_stock_df
        sku_master = sku_master_df
    else:
        try:
            branch_inventory = pd.read_csv(os.path.join(data_path, "Branch_Inventory.csv"))
            warehouse_stock = pd.read_csv(os.path.join(data_path, "Warehouse_Stock.csv"))
            sku_master = pd.read_csv(os.path.join(data_path, "SKU_Master.csv"))
        except FileNotFoundError as e:
            print(f"Error loading data: {e}. Make sure the CSV files are in the '{data_path}' directory.")
            return None, None, None, None

    # --- 2. Merge DataFrames for a complete view ---
    merged_data = pd.merge(branch_inventory, sku_master, on='SKU')
    merged_data = pd.merge(merged_data, warehouse_stock, on='SKU')

    # --- 3. Identify Branch Requirement ---
    merged_data['ReorderQty'] = merged_data.apply(
        lambda row: max(0, row['Max_Stock'] - row['Branch_Stock']) if row['Branch_Stock'] < row['Min_Stock'] else 0,
        axis=1
    )

    # --- 4. Allocate Stock & Create LPO ---
    transfer_orders_list = []
    lpo_needs_list = []
    lpo_trigger_transfers_list = []
    available_warehouse_stock = warehouse_stock.set_index('SKU')['Warehouse_Stock'].to_dict()
    reorder_df = merged_data[merged_data['ReorderQty'] > 0].sort_values(by='SKU')

    for _, row in reorder_df.iterrows():
        sku = row['SKU']
        reorder_qty = row['ReorderQty']
        
        # Capture initial warehouse stock for this SKU before any deductions for this specific reorder
        initial_warehouse_stock_for_sku = available_warehouse_stock.get(sku, 0)

        fulfillable_qty = min(reorder_qty, initial_warehouse_stock_for_sku)

        if fulfillable_qty > 0:
            transfer_orders_list.append({
                'SKU': sku,
                'From_Warehouse': 'WH01',
                'To_Branch': row['Branch'],
                'Min_Stock': row['Min_Stock'],
                'Max_Stock': row['Max_Stock'],
                'Branch_Stock': row['Branch_Stock'],
                'Transfer_Qty': fulfillable_qty,
                'Warehouse_Stock': initial_warehouse_stock_for_sku  # Stock before this specific transfer
            })
            available_warehouse_stock[sku] -= fulfillable_qty

        lpo_shortfall = reorder_qty - fulfillable_qty
        if lpo_shortfall > 0:
            lpo_needs_list.append({
                'SKU': sku, 'Required_Qty': lpo_shortfall, 'Vendor': row['Vendor']
            })

            # Capture LPO trigger details for the new sheet
            reason = "Partial Allocation" if fulfillable_qty > 0 else "Warehouse Out of Stock"
            lpo_trigger_transfers_list.append({
                'SKU': sku,
                'Branch': row['Branch'],
                'ReorderQty': reorder_qty,
                'Transfer_Qty_from_WH': fulfillable_qty,
                'Warehouse_Stock_Before_Transfer': initial_warehouse_stock_for_sku, # Use the captured initial stock
                'Warehouse_Stock_After_Transfer': available_warehouse_stock.get(sku, 0), # This is the stock after deduction
                'LPO_Shortfall': lpo_shortfall,
                'Reason': reason
            })

    transfer_orders_df = pd.DataFrame(transfer_orders_list)
    if not transfer_orders_df.empty:
        transfer_orders_df = transfer_orders_df[[
            'SKU', 'From_Warehouse', 'To_Branch', 'Min_Stock', 'Max_Stock',
            'Branch_Stock', 'Transfer_Qty', 'Warehouse_Stock'
        ]]
    lpo_needs_df = pd.DataFrame(lpo_needs_list)
    if not lpo_needs_df.empty:
        lpo_needs_df = lpo_needs_df.groupby(['SKU', 'Vendor'])['Required_Qty'].sum().reset_index()

    # --- 5. Identify Excess Stock based on Days of Stock (DOS) ---
    # Calculate Average Daily Sales (ADS) from Sales_30D
    merged_data['Avg_Daily_Sales'] = merged_data['Sales_30D'] / 30

    # Rename ReorderQty to Total_Branch_Requirement for clarity
    merged_data.rename(columns={'ReorderQty': 'Total_Branch_Requirement'}, inplace=True)

    # Calculate Target Excess Stock and Excess Quantity
    merged_data['Target_Excess_Stock'] = merged_data.apply(
        lambda row: row['Avg_Daily_Sales'] * EXCESS_DOS_THRESHOLD if row['Avg_Daily_Sales'] > 0 else 0,
        axis=1
    )
    merged_data['ExcessQty'] = merged_data.apply(
        lambda row: max(0, row['Branch_Stock'] - row['Target_Excess_Stock']),
        axis=1
    )

    # Create the specific columns requested for the output file
    merged_data['70D Target(daily*70)'] = merged_data['Target_Excess_Stock']
    merged_data['Excess(branch stock - 70D target)'] = merged_data['ExcessQty']

    excess_stock_df = merged_data[merged_data['ExcessQty'] > 0][[
        'Branch', 'SKU', 'Product_Name', 'Branch_Stock', 'Min_Stock', 'Max_Stock',
        'Total_Branch_Requirement', 'Sales_30D', 'Avg_Daily_Sales',
        'Target_Excess_Stock', 'ExcessQty', '70D Target(daily*70)', 'Excess(branch stock - 70D target)'
    ]]

    # Round the calculated fields to 2 decimal places
    for col in ['Avg_Daily_Sales', 'Target_Excess_Stock', 'ExcessQty', '70D Target(daily*70)', 'Excess(branch stock - 70D target)']:
        if col in excess_stock_df.columns:
            excess_stock_df[col] = excess_stock_df[col].round(2)

    # --- 6. Save All Outputs ---
    os.makedirs(output_path, exist_ok=True)
    lpo_trigger_transfers_df = pd.DataFrame(lpo_trigger_transfers_list)
    if not lpo_trigger_transfers_df.empty:
        lpo_trigger_transfers_df = lpo_trigger_transfers_df[[
            'SKU', 'Branch', 'ReorderQty', 'Transfer_Qty_from_WH',
            'Warehouse_Stock_After_Transfer',
            'LPO_Shortfall', 'Reason'
        ]]

    # Save Transfer Orders to an Excel file with multiple sheets
    transfer_orders_excel_path = os.path.join(output_path, "Transfer_Orders.xlsx")
    with pd.ExcelWriter(transfer_orders_excel_path, engine='openpyxl') as writer:
        transfer_orders_df.to_excel(writer, sheet_name='All_Transfer_Orders', index=False)
        if not lpo_trigger_transfers_df.empty:
            lpo_trigger_transfers_df.to_excel(writer, sheet_name='LPO_Trigger_Transfers', index=False)
    lpo_needs_df.to_csv(os.path.join(output_path, "LPO_Needs.csv"), index=False)
    excess_stock_df.to_csv(os.path.join(output_path, "Excess_Stock.csv"), index=False)

    print(f"Replenishment engine run complete. Outputs saved to '{output_path}'.")
    print(f"- Total LPOs created: {len(lpo_needs_df)}")
    print(f"- Total excess stock instances identified: {len(excess_stock_df)}")

    return merged_data, transfer_orders_df, lpo_needs_df, excess_stock_df

if __name__ == '__main__':
    run_replenishment_engine()
