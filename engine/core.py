
import pandas as pd
import os

# Define a configurable threshold for excess stock in days of supply
EXCESS_DOS_THRESHOLD = 60 # Defaulting to 60 days, can be adjusted

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
    available_warehouse_stock = warehouse_stock.set_index('SKU')['Warehouse_Stock'].to_dict()
    reorder_df = merged_data[merged_data['ReorderQty'] > 0].sort_values(by='SKU')

    for _, row in reorder_df.iterrows():
        sku = row['SKU']
        reorder_qty = row['ReorderQty']
        fulfillable_qty = min(reorder_qty, available_warehouse_stock.get(sku, 0))

        if fulfillable_qty > 0:
            transfer_orders_list.append({
                'SKU': sku, 'From_Warehouse': 'WH01', 'To_Branch': row['Branch'], 'Transfer_Qty': fulfillable_qty
            })
            available_warehouse_stock[sku] -= fulfillable_qty

        lpo_shortfall = reorder_qty - fulfillable_qty
        if lpo_shortfall > 0:
            lpo_needs_list.append({
                'SKU': sku, 'Required_Qty': lpo_shortfall, 'Vendor': row['Vendor']
            })

    transfer_orders_df = pd.DataFrame(transfer_orders_list)
    lpo_needs_df = pd.DataFrame(lpo_needs_list)
    if not lpo_needs_df.empty:
        lpo_needs_df = lpo_needs_df.groupby(['SKU', 'Vendor'])['Required_Qty'].sum().reset_index()

    # --- 5. Identify Excess Stock based on Days of Stock (DOS) ---
    # Calculate Average Daily Sales (ADS) from Sales_30D
    merged_data['Avg_Daily_Sales'] = merged_data['Sales_30D'] / 30

    # Calculate target stock based on EXCESS_DOS_THRESHOLD
    # Handle cases where Avg_Daily_Sales is 0 to avoid division by zero or unrealistic excess
    merged_data['Target_Excess_Stock'] = merged_data.apply(
        lambda row: row['Avg_Daily_Sales'] * EXCESS_DOS_THRESHOLD if row['Avg_Daily_Sales'] > 0 else 0,
        axis=1
    )

    # Calculate Excess Quantity
    merged_data['ExcessQty'] = merged_data.apply(
        lambda row: max(0, row['Branch_Stock'] - row['Target_Excess_Stock']),
        axis=1
    )

    excess_stock_df = merged_data[merged_data['ExcessQty'] > 0][[
        'Branch', 'SKU', 'Product_Name', 'Branch_Stock', 'Sales_30D', 'Avg_Daily_Sales', 'Target_Excess_Stock', 'ExcessQty'
    ]]

    # --- 6. Save All Outputs ---
    os.makedirs(output_path, exist_ok=True)
    transfer_orders_df.to_csv(os.path.join(output_path, "Transfer_Orders.csv"), index=False)
    lpo_needs_df.to_csv(os.path.join(output_path, "LPO_Needs.csv"), index=False)
    excess_stock_df.to_csv(os.path.join(output_path, "Excess_Stock.csv"), index=False)

    print(f"Replenishment engine run complete. Outputs saved to '{output_path}'.")
    print(f"- Total LPOs created: {len(lpo_needs_df)}")
    print(f"- Total excess stock instances identified: {len(excess_stock_df)}")

    return merged_data, transfer_orders_df, lpo_needs_df, excess_stock_df

if __name__ == '__main__':
    run_replenishment_engine()
