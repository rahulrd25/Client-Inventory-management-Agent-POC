import streamlit as st
import pandas as pd
import time # Import time module
from engine.core import run_replenishment_engine
from frontend.utils import apply_custom_css
from frontend.ui_components import set_page_config, render_header, render_file_uploader, render_results_section

# --- Define Application States ---
UPLOAD_STATE = "upload"
FILE_UPLOAD_CONFIRMATION_STATE = "file_upload_confirmation"
READY_TO_PROCESS_STATE = "ready_to_process"
PROCESSING_STATE = "processing"
RESULTS_STATE = "results"
WELCOME_STATE = "welcome"

# --- Page Configuration ---
set_page_config()

# --- Custom CSS for styling and alignment ---
apply_custom_css()

# --- Session State Initialization ---
# Initialize session state for results if not already present
if 'transfer_orders' not in st.session_state:
    st.session_state.transfer_orders = pd.DataFrame()
    st.session_state.lpo_needs = pd.DataFrame()
    st.session_state.excess_stock = pd.DataFrame()

# Initialize app state
if 'app_state' not in st.session_state:
    st.session_state.app_state = WELCOME_STATE

# Initialize dataframes in session state
if 'branch_df' not in st.session_state:
    st.session_state.branch_df = None
if 'warehouse_df' not in st.session_state:
    st.session_state.warehouse_df = None
if 'sku_master_df' not in st.session_state:
    st.session_state.sku_master_df = None

# Initialize upload attempted flag
if 'upload_attempted' not in st.session_state:
    st.session_state.upload_attempted = False

# --- Conditional Rendering based on App State ---

if st.session_state.app_state == WELCOME_STATE:
    render_header()
    st.markdown("""
    <div style='text-align: center; font-size: 2rem; margin-top: 1rem; margin-bottom: 1rem; color: black; font-weight: bold;'>
    Welcome!
    </div>
    <div style='text-align: center; font-size: 1.3rem; margin-bottom: 2rem; color: Purple; font-weight: bold; max-width: 600px; margin-left: auto; margin-right: auto;'>
    <div style='text-align: left;'>I'm here to help you to optimize inventory levels by:
    <ul>
        <li><i class="fa-solid fa-chart-line"></i> Identifying low-stock items</li>
        <li><i class="fa-solid fa-warehouse"></i> Managing stock allocation from the central warehouse</li>
        <li><i class="fa-solid fa-file-invoice"></i> Generating Local Purchase Orders (LPOs) when needed</li>
        <li><i class="fa-solid fa-boxes-stacked"></i> Highlighting excess inventory across branches</li>
    </ul>
    Let's make sure your shelves stay full, efficiently and effortlessly.
    </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start", key="start_button"):
        st.session_state.app_state = UPLOAD_STATE
        st.rerun()

elif st.session_state.app_state == UPLOAD_STATE:
    render_header()
    st.markdown("""
    <div style='text-align: center; font-size: 1.8rem; margin-top: 1rem; margin-bottom: 1rem; color: black; font-weight: bold;'>
    Let's get you started!
    </div>
    <div style='text-align: center; font-size: 1.2rem; margin-bottom: 2rem; color: #555555;'>
    Please upload your data here
    </div>
    """, unsafe_allow_html=True)
    branch_df, warehouse_df, sku_master_df, all_required_files_uploaded = render_file_uploader()

    # Store uploaded dataframes in session state
    st.session_state.branch_df = branch_df
    st.session_state.warehouse_df = warehouse_df
    st.session_state.sku_master_df = sku_master_df

    if all_required_files_uploaded:
        st.session_state.app_state = FILE_UPLOAD_CONFIRMATION_STATE
        st.rerun()
    # Display warning if upload attempted and not all files are present
    if st.session_state.upload_attempted and not all_required_files_uploaded:
        st.markdown("""
        <div style='text-align: center; font-size: 1rem; margin-top: 1rem; color: red; font-weight: bold;'>
        Please upload all three required files: Branch_Inventory.csv, Warehouse_Stock.csv, SKU_Master.csv
        </div>
        """, unsafe_allow_html=True)
    
    
elif st.session_state.app_state == FILE_UPLOAD_CONFIRMATION_STATE:
    render_header()
    # The file uploader already displays the "Uploaded files: ..." message
    # We just need to ensure the dataframes are still in session state for the next step
    # No need to call render_file_uploader again, as it would re-render the uploader widget

    # Brief pause to allow user to see the uploaded files message
    time.sleep(5) # Adjust delay as needed

    # Automatically transition to the next state
    st.session_state.app_state = READY_TO_PROCESS_STATE
    st.rerun()

elif st.session_state.app_state == READY_TO_PROCESS_STATE:
    render_header()
    st.markdown("""
    <div style='text-align: center; font-size: 1.8rem; margin-top: 1rem; margin-bottom: 1rem; color: black; font-weight: bold;'>
    Files Ready for Optimization!
    </div>
    <div style='text-align: center; font-size: 1.2rem; margin-bottom: 3rem; color: #555555;'>
    Your data has been successfully uploaded. Click the button below to initiate the replenishment process.
    </div>
    """, unsafe_allow_html=True)

    if st.button("✨ Initiate Optimization ✨", key="initiate_optimization_button"):
        st.session_state.app_state = PROCESSING_STATE
        st.rerun()

elif st.session_state.app_state == PROCESSING_STATE:
    render_header()

    PROCESSING_MESSAGES = [
        "Analyzing inventory data...",
        "Identifying stock requirements...",
        "Allocating stock from warehouse...",
        "Generating Local Purchase Orders (LPOs)...",
        "Detecting excess inventory...",
        "Finalizing replenishment plan..."
    ]

    # Use placeholders
    progress_text = st.empty()
    progress_bar = st.progress(0)

    # Simulate step-by-step updates
    for step, message in enumerate(PROCESSING_MESSAGES):
        progress_text.markdown(f"<div class='processing-step'>{message}</div>", unsafe_allow_html=True)
        progress_bar.progress((step + 1) / len(PROCESSING_MESSAGES))
        time.sleep(0.8)  # Simulated delay

    # Run the replenishment engine (actual heavy computation)
    with st.spinner("Running core replenishment engine..."):
        try:
            merged_data, transfer_orders, lpo_needs, excess_stock = run_replenishment_engine(
                branch_inventory_df=st.session_state.branch_df,
                warehouse_stock_df=st.session_state.warehouse_df,
                sku_master_df=st.session_state.sku_master_df,
                output_path="outputs"
            )

            st.session_state.transfer_orders = transfer_orders
            st.session_state.lpo_needs = lpo_needs
            st.session_state.excess_stock = excess_stock

            st.session_state.app_state = RESULTS_STATE
            st.rerun()

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
            st.exception(e)
            st.session_state.app_state = UPLOAD_STATE # Revert to upload state on error
            st.rerun()

elif st.session_state.app_state == RESULTS_STATE:
    render_header() # Keep header visible in results
    render_results_section()

    st.markdown("<br><br><br><br>", unsafe_allow_html=True) # Adds more line breaks for spacing

    # Add a button to reset the app
    if st.button("Start Over", key="reset_button"):
        st.session_state.app_state = UPLOAD_STATE
        # Clear uploaded files and results to ensure a clean start
        st.session_state.branch_df = None
        st.session_state.warehouse_df = None
        st.session_state.sku_master_df = None
        st.session_state.transfer_orders = pd.DataFrame()
        st.session_state.lpo_needs = pd.DataFrame()
        st.session_state.excess_stock = pd.DataFrame()
        st.rerun()