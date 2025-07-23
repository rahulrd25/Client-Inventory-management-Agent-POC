import streamlit as st
import pandas as pd
import base64
import os


def load_file(f):
    """
    Loads a file (CSV or Excel) into a pandas DataFrame.
    """
    if f.name.endswith(".csv"):
        return pd.read_csv(f)
    else:
        return pd.read_excel(f)


def get_logo_base64(logo_path="logo.svg"):
    """
    Reads logo.svg and encodes it to base64 for embedding.
    """
    try:
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        st.error(f"{logo_path} not found in the root directory. Please ensure it's there.")
        st.stop()


def apply_custom_css():
    """
    Applies custom CSS for styling and alignment.
    """
    st.markdown("""
    <style>
        /* Hide Streamlit's default header, footer, and main menu */
        #MainMenu, footer, header {visibility: hidden;}


        /* Main app background with green-blue gradient */
        .stApp {
            background: linear-gradient(135deg, #F0F2F5 0%, #FFFFFF 100%); /* Whitish gradient */
            font-family: 'Inter', sans-serif;
            color: #000000; /* Default text color to black */
        }


        /* Adjust main content block width and padding */
        .main .block-container {
            max-width: 900px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }


        /* Header container for logo and title to be side-by-side */
        .header-flex-container {
            display: flex;
            align-items: center; /* Vertically center items */
            justify-content: center; /* Center the whole block horizontally */
            margin-bottom: 2rem;
        }


        .header-flex-container img {
            margin-right: 20px; /* Space between logo and title */
        }


        .header-flex-container h1 {
            font-size: 2.7rem; /* Big title */
            font-weight: 700;
            color: #000000; /* Black */
            margin: 0; /* Remove default margin */
            line-height: 1.2; /* Adjust line height */
            white-space: nowrap; /* Prevent text from wrapping */
            overflow: hidden; /* Hide overflowing text */
            text-overflow: ellipsis; /* Add ellipsis for overflowing text */
        }


        /* Styling for subheaders (h2) */
        h2 {
            color: #000000; /* Black font color */
            font-weight: 500; /* Make it bold */
            font-size: 1.2rem; /* Slightly larger font size */
            margin-top: 2rem;
            margin-bottom: 2rem;
        }


        /* Styling for buttons */
        .stButton > button {
            width: 30%; /* Even smaller width */
            background: #0000FF; /* Blue background */
            color: #FFFFFF !important; /* White text for contrast */
            font-size: 1rem;
            font-weight: 700; /* Made bolder */
            border: none;
            border-radius: 10px; /* Slightly less rounded */
            padding: 1rem 1rem; /* Even smaller padding */
            transition: 0.3s;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Added shadow */
            display: block; /* Make it a block element */
            margin: 0 auto; /* Center the button */
        }


        .stButton > button:hover {
            background: #000000; /* Black on hover */
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3); /* Larger shadow on hover */
            color: #FFFFFF !important; /* White text on hover */
        }


        /* Ensure the text inside the main button is white */
        .stButton > button > span {
            color: white !important;
        }


        .stButton > button:disabled {
            background: #000000; /* Black when disabled */
            color: #FFFFFF; /* White text when disabled */
            cursor: not-allowed;
            box-shadow: none;
        }


        .stButton > button:disabled:hover {
            background: #000000; /* Keep black background on hover when disabled */
            box-shadow: none; /* Keep no shadow on hover when disabled */
            color: #FFFFFF; /* Keep white text on hover when disabled */
        }


        /* Styling for download button text */
        .stDownloadButton > button {
            background: #1E90FF; /* Vibrant Blue */
            color: #FFFFFF; /* White text */
            font-weight: 700;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            transition: 0.3s;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            width: 100%; /* Make button fill column */
        }


        .stDownloadButton > button:hover {
            background: #0056b3; /* Darker blue on hover */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }


        .stDownloadButton > button > span {
            color: #FFFFFF !important;
        }


        


        


        /* Styling for success messages */
        .stSuccess {
            background-color: #e8f5e9; /* Light green */
            color: #2e7d32; /* Dark green */
            border-left: 5px solid #2e7d32;
            padding: 0.75rem 1rem;
            border-radius: 5px;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }


        /* Styling for error messages */
        .stError {
            background-color: #ffebee; /* Light red */
            color: #d32f2f; /* Dark red */
            border-left: 5px solid #d32f2f;
            padding: 0.75rem 1rem;
            border-radius: 5px;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }


        /* Styling for dataframes */
        .stDataFrame {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }


        /* Specific alignment for subheaders in upload columns */
        .st-emotion-cache-10trblm p {
            text-align: left; /* Align subheader text to left */
        }


        /* Hide the uploaded file list (more aggressive) */
        .stFileUploader > div:not([data-testid="stFileUploaderDropzone"]) {
            display: none;
        }


        /* Styling for file uploader dropzone background */
        section[data-testid="stFileUploaderDropzone"] {
            background-color: #1E90FF !important; /* Vibrant Blue */
            color: white !important; /* White text */
        }


        /* Ensure text within the dropzone is white */
        section[data-testid="stFileUploaderDropzone"] div,
        section[data-testid="stFileUploaderDropzone"] span,
        section[data-testid="stFileUploaderDropzone"] small {
            color: white !important;
        }


        


        
    /* Styling for processing messages (st.info) */
        div[data-testid="stInfo"] {
            background-color: transparent !important;
        }


        div[data-testid="stInfo"] p {
            color: black !important;
        }
    </style>
    """
    , unsafe_allow_html=True)