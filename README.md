# Client Inventory Management Agent (Replenishment Engine)

This project implements a Replenishment Engine designed to optimize inventory levels across pharmacy branches. It automates the identification of stock requirements, manages stock allocation from a central warehouse, facilitates external procurement (Local Purchase Orders - LPOs), and identifies excess inventory.

## Key Features

*   **Identifies Branch Replenishment Needs:** Determines which products at each branch require additional stock based on minimum inventory levels and dynamically calculated `Min_Stock` and `Max_Stock` (based on 30-day sales and lead time).
*   **Stock Allocation & LPO Generation:** Allocates available stock from the central warehouse to fulfill branch requirements. For any unfulfilled demand, it generates Local Purchase Orders (LPOs) for external procurement.
*   **Excess Stock Identification:** Identifies and flags products at branches that hold inventory exceeding optimal levels, using a "Days of Stock" (DOS) metric.

## Operational Logic Overview

The engine processes inventory data through a systematic flow:

1.  **Identify Branch Replenishment Needs:** Calculates `ReorderQty` for each product at each branch if `Branch_Stock` is below `Min_Stock`. `Min_Stock` and `Max_Stock` are dynamically calculated based on `Sales_30D` and `Lead_Time_Days`.
2.  **Check Warehouse for Stock Availability:** Attempts to fulfill `ReorderQty` from `Warehouse_Stock`. If warehouse stock is insufficient, the remaining quantity is flagged for an LPO.
3.  **Create Transfer Orders:** Generates a detailed list of products to be moved from the central warehouse to specific branches.
4.  **Prepare and Flag LPO Needs:** Consolidates and lists all products requiring external procurement due to insufficient warehouse stock.
5.  **Identify Excess Stock:** Calculates excess stock using a "Days of Stock" (DOS) metric, based on `Branch_Stock` and `Sales_30D`.

## Input Files

The application requires the following CSV files to be uploaded:

*   `Branch_Inventory.csv`: Contains current stock levels for products at each branch.
*   `Warehouse_Stock.csv`: Contains current stock levels in the central warehouse.
*   `SKU_Master.csv`: Contains master data for SKUs, including `Min_Stock`, `Max_Stock`, `Sales_30D`, `Lead_Time_Days`, and `Vendor` information.

## Output Files

Upon completion of each replenishment engine run, the following CSV files are generated in the `outputs/` directory:

*   `Transfer_Orders.csv`: Details all products and quantities to be transferred from the central warehouse to specific branches.
*   `LPO_Needs.csv`: Lists all products, required quantities, and associated vendors for external procurement.
*   `Excess_Stock.csv`: Identifies products at branches that are overstocked, including the calculated excess quantity based on Days of Stock.

## Demo Video

Watch a quick demonstration of the Replenishment Engine in action:

[![Loom Video](https://www.loom.com/assets/img/loom-video-thumb.png)](https://www.loom.com/share/211c44e0825e4365aaf13e7d0b943c2d?sid=b4f213d5-d8e5-4a02-9ae0-154dd353f4c0)

## How to Run the Application

This application is built using Streamlit.

1.  **Ensure Python Environment:** Make sure you have Python 3.8+ installed. It's recommended to use a virtual environment.
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Assuming `requirements.txt` exists and contains `streamlit`, `pandas`, etc.)
3.  **Run the Streamlit App:**
    ```bash
    streamlit run streamlit_app.py
    ```
    This will open the application in your web browser.
