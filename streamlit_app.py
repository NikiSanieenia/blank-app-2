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
uploaded_approved = st.file_uploader("Upload Approved Applications File", type=["csv", "xlsx", "xls"])


st.subheader("Submitted Applications File")
uploaded_submitted = st.file_uploader("Upload Submitted Applications File", type=["csv", "xlsx", "xls"])


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
            # Display all uploaded files
            st.subheader("Uploaded Files Preview:")
            
            # Display outreach file
            if uploaded_outreach:
                outreach_preview = pd.read_excel(uploaded_outreach)
                st.write("Preview of Member Outreach File:")
                st.dataframe(outreach_preview)
            
            # Display event debrief file
            if uploaded_event:
                event_preview = pd.read_excel(uploaded_event)
                st.write("Preview of Event Debrief File:")
                st.dataframe(event_preview)
            
            # Display approved applications file
            if uploaded_approved:
                approved_preview = pd.read_excel(uploaded_approved) if uploaded_approved.name.endswith(('.xlsx', '.xls')) else pd.read_csv(uploaded_approved)
                st.write("Preview of Approved Applications File:")
                st.dataframe(approved_preview)
            
            # Display submitted applications file
            if uploaded_submitted:
                submitted_preview = pd.read_excel(uploaded_submitted) if uploaded_submitted.name.endswith(('.xlsx', '.xls')) else pd.read_csv(uploaded_submitted)
                st.write("Preview of Submitted Applications File:")
                st.dataframe(submitted_preview)

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
            
            # Convert date columns to datetime
            outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
            event_df['Date of the Event'] = pd.to_datetime(event_df['Date of the Event'], errors='coerce')

            # Perform a left join with approved applications using specified keys
            approved_df = pd.read_excel(uploaded_approved) if uploaded_approved.name.endswith(('.xlsx', '.xls')) else pd.read_csv(uploaded_approved)
            final_df = outreach_df.merge(
                approved_df,
                how='left',
                left_on='Name',  # Column in outreach_df
                right_on='memberName'  # Column in approved_df
            )
            
            # Display the final result
            st.write("Final Merged DataFrame:")
            st.dataframe(final_df)

            st.success("Data processing completed successfully!")

        except Exception as e:
            st.error(f"An error occurred during data processing: {e}")
