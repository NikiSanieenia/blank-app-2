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

st.subheader("Event Debrief File")
uploaded_event = st.file_uploader("Upload Event Debrief File (Excel)", type=["xlsx"])

st.subheader("Approved Applications File")
uploaded_approved = st.file_uploader("Upload Approved Applications File (CSV)", type=["csv"])

st.subheader("Submitted Applications File")
uploaded_submitted = st.file_uploader("Upload Submitted Applications File (CSV)", type=["csv"])

# Growth officer mapping dictionary
growth_officer_mapping = {
    'Ileana': 'Ileana Heredia',
    'ileana': 'Ileana Heredia',
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

# Helper function to read files
def load_excel(file):
    try:
        return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        st.error(f"An error occurred while reading the Excel file: {e}")
        return pd.DataFrame()

def load_csv(file):
    try:
        return pd.read_csv(file)
    except Exception as e:
        st.error(f"An error occurred while reading the CSV file: {e}")
        return pd.DataFrame()

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
            # Load Member Outreach and Event files
            outreach_df = load_excel(uploaded_outreach)
            event_df = load_excel(uploaded_event)
            
            # Apply growth officer mapping
            if 'Growth Officer' in outreach_df.columns:
                outreach_df['Growth Officer'] = outreach_df['Growth Officer'].map(growth_officer_mapping).fillna(outreach_df['Growth Officer'])
                st.write("Growth Officer names mapped successfully!")

            # Convert date columns to datetime
            outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
            event_df['Date of the Event'] = pd.to_datetime(event_df['Date of the Event'], errors='coerce')

            # Perform a left join with a custom condition for the 10-day range
            def join_with_tolerance(outreach_df, event_df, tolerance_days=10):
                outreach_df = outreach_df.dropna(subset=['Date']).copy()
                event_df = event_df.dropna(subset=['Date of the Event']).copy()

                # Add a key for Cartesian product merge
                outreach_df['key'] = 1
                event_df['key'] = 1

                # Create the Cartesian product and filter for tolerance range
                merged = pd.merge(outreach_df, event_df, on='key').drop(columns=['key'])
                merged['date_diff'] = (merged['Date of the Event'] - merged['Date']).dt.days

                # Filter to only include events within the tolerance range
                merged = merged[(merged['date_diff'] >= 0) & (merged['date_diff'] <= tolerance_days)]

                # Keep only the closest event for each outreach date
                closest_events = merged.loc[merged.groupby('Date')['date_diff'].idxmin()]

                # Perform a left join to retain all outreach records
                result = pd.merge(outreach_df, closest_events, how='left', on=['Date'], suffixes=('', '_event'))
                return result

            # Join outreach and event data
            event_outreach_df = join_with_tolerance(outreach_df, event_df)
            st.write("Merged outreach and event data (Left Join):")
            st.dataframe(event_outreach_df)

            # Load Approved and Submitted Applications files
            approved_df = load_csv(uploaded_approved)
            submitted_df = load_csv(uploaded_submitted)

            # Perform a left join with Approved Applications
            approved_merged_df = pd.merge(
                event_outreach_df,
                approved_df,
                how='left',
                left_on='Outreach Name',
                right_on='memberName',
                suffixes=('', '_approved')
            )
            st.write("Merged data with Approved Applications (Left Join):")
            st.dataframe(approved_merged_df)

            # Perform a left join with Submitted Applications
            submitted_merged_df = pd.merge(
                event_outreach_df,
                submitted_df,
                how='left',
                left_on='Outreach Name',
                right_on='memberName',
                suffixes=('', '_submitted')
            )
            st.write("Merged data with Submitted Applications (Left Join):")
            st.dataframe(submitted_merged_df)

            st.success("All data merges completed successfully!")

        except Exception as e:
            st.error(f"An error occurred during data processing: {e}")
