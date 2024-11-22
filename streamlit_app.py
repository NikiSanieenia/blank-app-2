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
uploaded_outreach = st.file_uploader("Upload Member Outreach File (Excel or CSV)", type=["xlsx", "csv"])

st.subheader("Event Debrief File")
uploaded_event = st.file_uploader("Upload Event Debrief File (Excel or CSV)", type=["xlsx", "csv"])

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

# Helper function for matching outreach and event data
def match_outreach_and_events(outreach_df, event_df, tolerance_days=10):
    matched_records = []
    unmatched_outreach = outreach_df.copy()
    unmatched_event = event_df.copy()

    for _, outreach_row in outreach_df.iterrows():
        outreach_date = outreach_row['Date']
        matching_events = event_df[
            (event_df['Date of the Event'] >= outreach_date - pd.Timedelta(days=tolerance_days)) &
            (event_df['Date of the Event'] <= outreach_date)
        ]
        if not matching_events.empty:
            combined_event_name = "/".join(matching_events['Event Name'].unique())
            combined_event_location = "/".join(matching_events['Location'].unique())
            combined_event_officer = "/".join(matching_events['Name'].unique())
            matched_records.append({
                'Outreach Date': outreach_date,
                'Growth Officer': outreach_row.get('Growth Officer', ''),
                'Outreach Name': outreach_row.get('Name', ''),
                'Occupation': outreach_row.get('Occupation', ''),
                'Email': outreach_row.get('Email', ''),
                'Date of the Event': matching_events['Date of the Event'].iloc[0],
                'Event Location': combined_event_location,
                'Event Name': combined_event_name,
                'Event Officer': combined_event_officer,
                'Select Your School': "/".join(matching_events['Select Your School'].unique()),
                'Request type?': "/".join(matching_events['Request type?'].unique()),
                'Audience': "/".join(matching_events['Audience'].unique())
            })
            unmatched_outreach = unmatched_outreach[unmatched_outreach['Date'] != outreach_row['Date']]
            unmatched_event = unmatched_event[~unmatched_event['Date of the Event'].isin(matching_events['Date of the Event'])]
        else:
            matched_records.append({
                'Outreach Date': outreach_date,
                'Growth Officer': outreach_row.get('Growth Officer', ''),
                'Outreach Name': outreach_row.get('Name', ''),
                'Occupation': outreach_row.get('Occupation', ''),
                'Email': outreach_row.get('Email', ''),
                'Date of the Event': None,
                'Event Location': None,
                'Event Name': None,
                'Event Officer': None,
                'Select Your School': None,
                'Request type?': None,
                'Audience': None
            })

    for _, event_row in unmatched_event.iterrows():
        matched_records.append({
            'Outreach Date': None,
            'Growth Officer': None,
            'Outreach Name': None,
            'Occupation': None,
            'Email': None,
            'Date of the Event': event_row['Date of the Event'],
            'Event Location': event_row['Location'],
            'Event Name': event_row['Event Name'],
            'Event Officer': event_row['Name'],
            'Select Your School': event_row['Select Your School'],
            'Request type?': event_row['Request type?'],
            'Audience': event_row['Audience']
        })

    return pd.DataFrame(matched_records)

# Helper function to read Excel or CSV files
def read_file(file):
    if file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    elif file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        st.error("Unsupported file type.")
        return pd.DataFrame()

# Submit button and processing
if st.button("Upload All Files to Drive and Process Data"):
    if not uploaded_outreach or not uploaded_event:
        st.error("Please upload both the Member Outreach and Event Debrief files.")
    else:
        try:
            outreach_df = read_file(uploaded_outreach)
            event_df = read_file(uploaded_event)

            # Standardize Growth Officer names
            outreach_df['Growth Officer'] = outreach_df['Growth Officer'].replace(growth_officer_mapping)

            # Convert date columns to datetime
            outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
            event_df['Date of the Event'] = pd.to_datetime(event_df['Date of the Event'], errors='coerce')

            # Perform matching
            matched_df = match_outreach_and_events(outreach_df, event_df)

            st.write("Matched Data:")
            st.dataframe(matched_df)

            st.success("Data processing completed successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
