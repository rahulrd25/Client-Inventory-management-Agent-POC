import os
from engine.core import run_replenishment_engine

def main():
    DATA_PATH = "data"
    OUTPUT_PATH = "outputs"

    required_files = ["Branch_Inventory.csv", "Warehouse_Stock.csv", "SKU_Master.csv"]
    all_files_exist = True
    for file_name in required_files:
        if not os.path.exists(os.path.join(DATA_PATH, file_name)):
            print(f"Error: Missing required data file: {os.path.join(DATA_PATH, file_name)}")
            all_files_exist = False

    if not all_files_exist:
        print("\nPlease run 'python generate_dummy_replenishment_data.py' to create the necessary data files.")
        print("Make sure to move the generated CSVs into the 'data/' directory if they are not created there directly.")
    else:
        print("All required data files found. Running replenishment engine...")
        merged_data, transfer_orders_df, lpo_needs_df, excess_stock_df = run_replenishment_engine(
            data_path=DATA_PATH,
            output_path=OUTPUT_PATH
        )
        if merged_data is not None:
            print("\nReplenishment process completed successfully.")
            print(f"Transfer Orders generated: {len(transfer_orders_df)}")
            print(f"LPO Needs identified: {len(lpo_needs_df)}")
            print(f"Excess Stock identified: {len(excess_stock_df)}")
        else:
            print("\nReplenishment process failed. Check error messages above.")

if __name__ == "__main__":
    main()