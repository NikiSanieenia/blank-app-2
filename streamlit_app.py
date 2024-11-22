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

# School mapping for sheet names
schools = [
    ('UTA', 'UT ARLINGTON'),
    ('SCU', 'SANTA CLARA'),
    ('UCLA', 'UCLA'),
    ('LMU', 'LMU'),
    ('Pepperdine', 'PEPPERDINE'),
    ('Irvine', 'UC IRVINE'),
    ('San Diego', 'UC SAN DIEGO'),
    ('SMC', 'SAINT MARY\'S'),
    ('Davis', 'UC DAVIS')
]

# Submit button and processing
if st.button("Process Data"):
    if not uploaded_outreach or not uploaded_event:
        st.error("Both files must be uploaded.")
    else:
        try:
            all_final_dfs = []
            total_rows_individual = 0  # To track the sum of rows from all individual DataFrames

            # Process each sheet in the outreach file
            for sheet_name, school in schools:
                outreach_df = pd.read_excel(uploaded_outreach, sheet_name=sheet_name)
                event_df = pd.read_excel(uploaded_event, sheet_name="Growth")  # Only read the "Growth" sheet

                # Standardize Growth Officer names using the mapping
                outreach_df['Growth Officer'] = outreach_df['Growth Officer'].replace(growth_officer_mapping)

                # Filter for relevant school in the events data
                events_df = event_df[event_df['Select Your School'].str.strip().str.upper() == school.upper()]

                # Convert date columns to datetime
                outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
                events_df['Date of the Event'] = pd.to_datetime(events_df['Date of the Event'], errors='coerce')

                # Drop rows with NaT in date columns
                outreach_df = outreach_df.dropna(subset=['Date'])
                events_df = events_df.dropna(subset=['Date of the Event'])

                # Match outreach records with events within a 10-day range
                matched_records = []
                unmatched_event = events_df.copy()

                for _, outreach_row in outreach_df.iterrows():
                    outreach_date = outreach_row['Date']

                    # Find events within 10 days after the outreach date
                    matching_events = events_df[
                        (events_df['Date of the Event'] >= outreach_date - pd.Timedelta(days=10)) &
                        (events_df['Date of the Event'] <= outreach_date)
                    ]

                    if not matching_events.empty:
                        combined_event_name = "/".join(matching_events['Event Name'].unique())
                        combined_event_location = "/".join(matching_events['Location'].unique())
                        combined_event_officer = "/".join(matching_events['Name'].unique())

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
                        unmatched_event = unmatched_event[
                            ~unmatched_event['Date of the Event'].isin(matching_events['Date of the Event'])
                        ]
                    else:
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

                # Add unmatched event records
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

                # Create final DataFrame and append to list
                final_df = pd.DataFrame(matched_records)
                final_df = final_df.dropna(
                    subset=['Outreach Date', 'Growth Officer', 'Outreach Name', 'Occupation', 'Email'], how='all'
                )
                all_final_dfs.append(final_df)
                total_rows_individual += len(final_df)

            # Concatenate all DataFrames
            Phase_1 = pd.concat(all_final_dfs, ignore_index=True)
            st.write("Processed Data:")
            st.dataframe(Phase_1)
            st.success(f"Data processed successfully! Total rows: {total_rows_individual}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
