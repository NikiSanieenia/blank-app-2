import streamlit as st
import pandas as pd

# Set up the page
st.set_page_config(page_title="UCU Google Drive File Uploader", layout="centered")

# Title and instructions
st.title("UCU Google Drive File Uploader")
st.write("Please upload the required files into their respective sections.")

# Custom styling with CSS
st.markdown("""
   <style>
       .stFileUploader {
           border: 1px solid #e6e6e6;
           padding: 10px;
           border-radius: 10px;
       }
       .stButton > button {
           background-color: #ff7f0e;
           color: white;
           font-weight: bold;
           padding: 10px 20px;
           border-radius: 10px;
       }
   </style>
""", unsafe_allow_html=True)

# File upload sections with headers
st.subheader("Member Outreach File")
uploaded_outreach = st.file_uploader("Upload Member Outreach File (Excel)", type=["xlsx"])
if uploaded_outreach:
    st.write("Uploaded Outreach File:", uploaded_outreach.name)

st.subheader("Event Debrief File")
uploaded_event = st.file_uploader("Upload Event Debrief File (Excel)", type=["xlsx"])
if uploaded_event:
    st.write("Uploaded Event Debrief File:", uploaded_event.name)

st.subheader("Approved Applications File")
uploaded_approved = st.file_uploader("Upload Approved Applications File", type=["csv", "xlsx", "xls"])
if uploaded_approved:
    st.write("Uploaded Approved Applications File:", uploaded_approved.name)

st.subheader("Submitted Applications File")
uploaded_submitted = st.file_uploader("Upload Submitted Applications File", type=["csv", "xlsx", "xls"])
if uploaded_submitted:
    st.write("Uploaded Submitted Applications File:", uploaded_submitted.name)

# Growth officer mapping dictionary
growth_officer_mapping = {
   'Ileana': 'Ileana Heredia',
   'BK': 'Brian Kahmar',
   'JR': 'Julia Racioppo',
   'Jordan': 'Jordan Richied',
   'VN': 'Veronica Nims',
   'vn': 'Veronica Nims',
   'Dom': 'Domenic Noto',
   'Megan': 'Megan Sterling',
   'Veronica': 'Veronica Nims',
   'SB': 'Sheena Barlow',
   'Julio': 'Julio Macias',
   'Mo': 'Monisha Donaldson'
}

# Helper function to read Excel files and add sheet name column
def read_excel_file(file, sheet_names):
    try:
        all_dfs = []
        for sheet in sheet_names:
            temp_df = pd.read_excel(file, sheet_name=sheet)
            temp_df['School Name'] = sheet  # Add a column for the sheet name
            all_dfs.append(temp_df)
        return pd.concat(all_dfs, ignore_index=True)
    except Exception as e:
        st.error(f"An error occurred while reading the Excel file: {e}")
        return pd.DataFrame()

# Updated join_with_tolerance function
def join_with_tolerance(outreach_df, event_df, tolerance_days=10):
    """
    Perform a left join between outreach and event data with a tolerance on dates and school name matching.

    Args:
        outreach_df (pd.DataFrame): The outreach data with 'Date' and 'School Name'.
        event_df (pd.DataFrame): The event data with 'Date of the Event' and 'School Name'.
        tolerance_days (int): The maximum allowed difference in days for a match.

    Returns:
        pd.DataFrame: The merged DataFrame with outreach and event data.
    """
    # Ensure both DataFrames have valid dates and school names
    outreach_df = outreach_df.dropna(subset=['Date', 'School Name']).copy()
    event_df = event_df.dropna(subset=['Date of the Event', 'School Name']).copy()

    # Normalize the school names for consistent matching
    outreach_df['School Name'] = outreach_df['School Name'].str.strip().str.lower()
    event_df['School Name'] = event_df['School Name'].str.strip().str.lower()

    # Add a key for Cartesian product merge
    outreach_df['key'] = 1
    event_df['key'] = 1

    # Create the Cartesian product
    merged = pd.merge(outreach_df, event_df, on='key').drop(columns=['key'])

    # Filter for school name match and date difference within tolerance
    merged = merged[
        (merged['School Name_x'] == merged['School Name_y']) &  # Match school names
        (merged['Date of the Event'] >= merged['Date']) &       # Event date >= Outreach date
        ((merged['Date of the Event'] - merged['Date']).dt.days <= tolerance_days)  # Within tolerance
    ]

    # Calculate date difference
    merged['date_diff'] = (merged['Date of the Event'] - merged['Date']).dt.days

    # Keep only the closest event for each outreach date
    closest_events = merged.loc[merged.groupby(['Date', 'School Name_x'])['date_diff'].idxmin()]

    # Perform a left join to retain all outreach records
    result = pd.merge(outreach_df, closest_events, 
                      how='left', 
                      on=['Date', 'School Name'], 
                      suffixes=('', '_event'))
    return result

# Submit button and processing
if st.button("Upload All Files to Drive and Process Data"):
    missing_files = []
    if not uploaded_outreach:
        missing_files.append("Member Outreach File")
    if not uploaded_event:
        missing_files.append("Event Debrief File")
    if not uploaded_approved:
        missing_files.append("Approved Applications File")
    if not uploaded_submitted:
        missing_files.append("Submitted Applications File")
    
    if missing_files:
        st.error(f"Error: The following files are missing: {', '.join(missing_files)}")
    else:
        try:
            # Sheet names to read for outreach data
            sheet_names = ['Irvine', 'SCU', 'LMU', 'UTA', 'SMC', 'Davis',
                           'Pepperdine', 'UCLA', 'GT', 'San Diego',
                           'MISC Schools', 'Template']
            
            # Combine outreach data with sheet name tracking
            outreach_df = read_excel_file(uploaded_outreach, sheet_names)
            st.write("Outreach data loaded successfully with sheet names!")
            
            # Load event data
            event_df = pd.read_excel(uploaded_event)
            st.write("Event data loaded successfully!")

            # Apply growth officer mapping
            if 'Growth Officer' in outreach_df.columns:
                outreach_df['Growth Officer'] = outreach_df['Growth Officer'].map(growth_officer_mapping).fillna(outreach_df['Growth Officer'])
                st.write("Growth Officer names mapped successfully!")

            # Convert date columns to datetime
            outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
            event_df['Date of the Event'] = pd.to_datetime(event_df['Date of the Event'], errors='coerce')

            # Join outreach and event data
            event_outreach_df = join_with_tolerance(outreach_df, event_df)

            st.write("Merged outreach and event data (Left Join):")
            st.dataframe(event_outreach_df)

            st.success("Data processing completed successfully!")

        except Exception as e:
            st.error(f"An error occurred during data processing: {e}")
