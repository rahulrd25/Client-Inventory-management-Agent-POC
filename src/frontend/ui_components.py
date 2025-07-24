import streamlit as st
import os
from .utils import get_logo_base64, load_file

def set_page_config():
    """
    Sets the Streamlit page configuration.
    """
    st.set_page_config(
        page_title="Replenishment Agent",
        page_icon=None, # No browser tab icon, as logo is on page
        layout="centered",
        initial_sidebar_state="collapsed",
    )

def render_header():
    """
    Renders the application header with logo and title.
    """
    logo_base64 = get_logo_base64()
    st.markdown(
        f"""
        <div class="header-flex-container">
            <img src="data:image/svg+xml;base64,{logo_base64}" alt="800 Pharmacy Logo" width="300">
            <h1>Replenishment Agent</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_file_uploader():
    """
    Renders the file uploader section and returns parsed dataframes.
    """
    uploaded_files = st.file_uploader(
        " ",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="all_files_uploader",
        label_visibility="hidden"
    )

    branch_df = None
    warehouse_df = None
    sku_master_df = None

    if uploaded_files:
        st.session_state.upload_attempted = True
        file_names = [file.name for file in uploaded_files]
        st.markdown(f"<p style=\"color:black;\">Uploaded files: {', '.join(file_names)}</p>", unsafe_allow_html=True)

        for file in uploaded_files:
            if "Branch_Inventory" in file.name:
                branch_df = load_file(file)
            elif "Warehouse_Stock" in file.name:
                warehouse_df = load_file(file)
            elif "SKU_Master" in file.name:
                sku_master_df = load_file(file)

    all_required_files_uploaded = (
        branch_df is not None and
        warehouse_df is not None and
        sku_master_df is not None
    )

    return branch_df, warehouse_df, sku_master_df, all_required_files_uploaded

def render_results_section():
    """
    Renders the results and download section.
    """
    if not st.session_state.transfer_orders.empty or \
       not st.session_state.lpo_needs.empty or \
       not st.session_state.excess_stock.empty:

        st.markdown("""
        <div style='
            background-color: #e6ffe6; /* Very light green */
            border: 2px solid #28a745; /* Green border */
            padding: 1rem; /* Reduced padding */
            margin: 1rem auto; /* Reduced margin, center horizontally */
            border-radius: 15px;
            font-weight: 700;
            color: #155724;
            font-size: 1.1rem; /* Reduced font size */
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Add shadow */
            max-width: 400px; /* Reduced max-width */
        '>
        ✅ Output Files are ready for download.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h2 style=\"text-align: center;\">Click to download Results</h2>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            if not st.session_state.transfer_orders.empty:
                st.download_button(
                    label="Transfer Orders",
                    data=open(os.path.join("outputs", "Transfer_Orders.xlsx"), "rb").read(),
                    file_name="Transfer_Orders.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_transfer_orders"
                )
            else:
                st.markdown("<p style='text-align: center; color: #666666;'>No transfer orders generated.</p>", unsafe_allow_html=True)

        with col2:
            if not st.session_state.lpo_needs.empty:
                st.download_button(
                    label="LPO Needs",
                    data=st.session_state.lpo_needs.to_csv(index=False).encode('utf-8'),
                    file_name="LPO_Needs.csv",
                    mime="text/csv",
                    key="download_lpo_needs"
                )
            else:
                st.markdown("<p style='text-align: center; color: #666666;'>No LPO needs identified.</p>", unsafe_allow_html=True)

        with col3:
            if not st.session_state.excess_stock.empty:
                st.download_button(
                    label="Excess Stock",
                    data=st.session_state.excess_stock.to_csv(index=False).encode('utf-8'),
                    file_name="Excess_Stock.csv",
                    mime="text/csv",
                    key="download_excess_stock"
                )
            else:
                st.markdown("<p style='text-align: center; color: #666666;'>No excess stock identified.</p>", unsafe_allow_html=True)
