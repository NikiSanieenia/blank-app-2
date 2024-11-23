import streamlit as st
import pandas as pd

# Set up the page
st.set_page_config(page_title="UCU Google Drive File Uploader", layout="centered")

# Title and instructions
st.title("UCU Google Drive File Uploader")
st.write("Please upload the required files into their respective sections.")

# File upload sections with headers
st.subheader("Member Outreach File")
uploaded_outreach = st.file_uploader("Upload Member Outreach File (Excel)", type=["xlsx"])

st.subheader("Event Debrief File")
uploaded_event = st.file_uploader("Upload Event Debrief File (Excel)", type=["xlsx"])

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

# Submit button and processing
if st.button("Upload All Files to Drive and Process Data"):
    if not uploaded_outreach or not uploaded_event:
        st.error("Please upload both the Member Outreach and Event Debrief files.")
    else:
        try:
            # Load data
            outreach_df = pd.read_excel(uploaded_outreach)
            event_df = pd.read_excel(uploaded_event)

            # Standardize Growth Officer names using the mapping
            outreach_df['Growth Officer'] = outreach_df['Growth Officer'].replace(growth_officer_mapping)

            # Convert date columns to datetime
            outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
            event_df['Date of the Event'] = pd.to_datetime(event_df['Date of the Event'], errors='coerce')

            # Drop rows with NaT in date columns
            outreach_df = outreach_df.dropna(subset=['Date'])
            event_df = event_df.dropna(subset=['Date of the Event'])

            # Initialize lists to store matched records
            matched_records = []
            unmatched_outreach = outreach_df.copy()
            unmatched_event = event_df.copy()

            # Match outreach records with events within a 10-day range before or after the outreach date
            for _, outreach_row in outreach_df.iterrows():
                outreach_date = outreach_row['Date']

                # Find events within the 10-day range
                matching_events = event_df[
                    (event_df['Date of the Event'] >= outreach_date - pd.Timedelta(days=10)) &
                    (event_df['Date of the Event'] <= outreach_date + pd.Timedelta(days=10))
                ]

                if not matching_events.empty:
                    # Combine event details for all matching events
                    combined_event_name = "/".join(matching_events['Event Name'].unique())
                    combined_event_location = "/".join(matching_events['Location'].unique())
                    combined_event_officer = "/".join(matching_events['Name'].unique())

                    # Create a combined row with outreach and event details
                    combined_row = {
                        'Outreach Date': outreach_row['Date'],
                        'Growth Officer': outreach_row.get('Growth Officer', ''),
                        'Outreach Name': outreach_row.get('Name', ''),
                        'Occupation': outreach_row.get('Occupation', ''),
                        'Email': outreach_row.get('Email', ''),
                        'Date of the Event': outreach_date,
                        'Event Location': combined_event_location,
                        'Event Name': combined_event_name,
                        'Event Officer': combined_event_officer,
                        'Select Your School': "/".join(matching_events['Select Your School'].unique()),
                        'Request type?': "/".join(matching_events['Request type?'].unique()),
                        'Audience': "/".join(matching_events['Audience'].unique())
                    }
                    matched_records.append(combined_row)

                    # Remove matched rows from unmatched records
                    unmatched_outreach = unmatched_outreach[unmatched_outreach['Date'] != outreach_row['Date']]
                    unmatched_event = unmatched_event[
                        ~unmatched_event['Date of the Event'].isin(matching_events['Date of the Event'])
                    ]
                else:
                    # No match found, add outreach record with NA for event details
                    unmatched_row = {
                        'Outreach Date': outreach_row['Date'],
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
                    }
                    matched_records.append(unmatched_row)

            # Add unmatched event records with NA for outreach details
            for _, event_row in unmatched_event.iterrows():
                unmatched_row = {
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
                }
                matched_records.append(unmatched_row)

            # Convert to DataFrame
            final_df = pd.DataFrame(matched_records)

            # Filter out rows where all outreach details are NaN
            final_df = final_df.dropna(subset=['Outreach Date', 'Growth Officer', 'Outreach Name', 'Occupation', 'Email'], how='all')

            st.write("Merged Outreach and Event Data:")
            st.dataframe(final_df)

            st.success("Data processing completed successfully!")
        except Exception as e:
            st.error(f"An error occurred during data processing: {e}")
