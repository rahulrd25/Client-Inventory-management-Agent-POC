import pandas as pd
import numpy as np
from random import choice, randint

# === Parameters ===
NUM_SKUS = 500
BRANCHES = ['BR001', 'BR002', 'BR003', 'BR004', 'BR005']
CATEGORIES = ['Medicine', 'Personal Care', 'Nutrition', 'Baby Care', 'OTC', 'Medical Devices']
VENDORS = ['VendorA', 'VendorB', 'VendorC', 'VendorD']
DAYS_OF_SALES_HISTORY = 30
SAFETY_STOCK_FACTOR = 1.5 # Min_Stock = Avg_Daily_Sales * SAFETY_STOCK_FACTOR
MAX_STOCK_FACTOR = 3.0    # Max_Stock = Min_Stock * MAX_STOCK_FACTOR

# A configurable threshold for excess stock in days of supply
EXCESS_DOS_THRESHOLD = 60 # Defaulting to 60 days for generation, can be changed in engine

# === 1. SKU Master Data ===
sku_ids = [f"SKU{str(i).zfill(4)}" for i in range(1, NUM_SKUS + 1)]
sku_master = pd.DataFrame({
    'SKU': sku_ids,
    'Product_Name': [f"Product {i}" for i in range(1, NUM_SKUS + 1)],
    'Category': [choice(CATEGORIES) for _ in range(NUM_SKUS)],
    'Vendor': [choice(VENDORS) for _ in range(NUM_SKUS)],
    'Lead_Time_Days': np.random.randint(2, 14, size=NUM_SKUS)
})
sku_master.to_csv("SKU_Master.csv", index=False)

# === 2. Branch Inventory Data (500 SKUs × 5 branches = 2500 rows) ===
branch_inventory_rows = []
for sku in sku_ids:
    for branch in BRANCHES:
        # Simulate 30 days of sales for each SKU at each branch
        daily_sales = [randint(0, 5) for _ in range(DAYS_OF_SALES_HISTORY)] # Random sales between 0 and 5 units/day
        sales_30d = sum(daily_sales)
        avg_daily_sales = sales_30d / DAYS_OF_SALES_HISTORY

        # Calculate Min_Stock and Max_Stock based on average daily sales
        # Ensure a minimum stock of at least 5 units to avoid zero min/max for slow movers
        min_stock = max(5, int(avg_daily_sales * SAFETY_STOCK_FACTOR * sku_master[sku_master['SKU'] == sku]['Lead_Time_Days'].iloc[0]))
        max_stock = max(min_stock + 10, int(min_stock * MAX_STOCK_FACTOR))

        # Generate current Branch_Stock
        # Introduce scenarios for excess stock based on DOS
        if avg_daily_sales > 0 and np.random.rand() < 0.1: # 10% chance of special case
            # Case 1: High Min_Stock, but also high Branch_Stock (triggering both reorder and excess)
            min_stock = int(avg_daily_sales * EXCESS_DOS_THRESHOLD * 1.5) # Very high min stock
            max_stock = int(min_stock * 1.2)
            branch_stock = int(min_stock * 0.9) # Below min, but still high
        elif avg_daily_sales > 0 and np.random.rand() < 0.15: # 15% chance of excess stock for items with sales
            # Ensure stock is significantly above the EXCESS_DOS_THRESHOLD
            target_stock_for_excess = int(avg_daily_sales * EXCESS_DOS_THRESHOLD * 1.2) # 20% above threshold
            branch_stock = randint(max(max_stock + 10, target_stock_for_excess), target_stock_for_excess + 50)
        else:
            # Normal stock generation, ensuring some are below min to trigger reorders
            branch_stock = randint(max(0, min_stock - 10), max_stock + 5)

        branch_inventory_rows.append({
            'SKU': sku,
            'Branch': branch,
            'Branch_Stock': branch_stock,
            'Min_Stock': min_stock,
            'Max_Stock': max_stock,
            'Sales_30D': sales_30d # Add 30-day sales to the output
        })
branch_inventory = pd.DataFrame(branch_inventory_rows)
branch_inventory.to_csv("Branch_Inventory.csv", index=False)

# === 3. Warehouse Stock (1 row per SKU) ===
warehouse_stock_levels = []
for _ in range(NUM_SKUS):
    r = np.random.rand()
    if r < 0.2: # 20% chance of very low stock
        warehouse_stock_levels.append(np.random.randint(0, 10))
    elif r < 0.5: # 30% chance of low stock
        warehouse_stock_levels.append(np.random.randint(10, 50))
    else: # 50% chance of moderate stock
        warehouse_stock_levels.append(np.random.randint(50, 200))

warehouse_stock = pd.DataFrame({
    'SKU': sku_ids,
    'Warehouse_Stock': warehouse_stock_levels
})
warehouse_stock.to_csv("Warehouse_Stock.csv", index=False)

# === 4. Transfer Orders Placeholder ===
transfer_orders = pd.DataFrame(columns=[
    'SKU', 'From_Warehouse', 'To_Branch', 'Transfer_Qty'
])
transfer_orders.to_csv("Transfer_Orders.csv", index=False)

# === 5. LPO Needs Placeholder ===
lpo_needs = pd.DataFrame(columns=[
    'SKU', 'Required_Qty', 'Vendor'
])
lpo_needs.to_csv("LPO_Needs.csv", index=False)

print("✅ CSV files generated successfully in current directory:")
print(" SKU_Master.csv")
print(" Branch_Inventory.csv")
print(" Warehouse_Stock.csv")
print(" Transfer_Orders.csv")
print(" LPO_Needs.csv")