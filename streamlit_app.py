import streamlit as st
import pandas as pd

# Set up the page
st.set_page_config(page_title="Google Drive File Uploader", layout="centered")

# Title and instructions
st.title("Google Drive File Uploader")
st.write("Please upload the required files into their respective sections.")

# File upload sections
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

# Helper function to process data
def process_data(outreach_file, event_file):
    try:
        # List of tuples containing sheet names and corresponding school names
        schools = [
            ('UTA', 'UT ARLINGTON'),
            ('SCU', 'SANTA CLARA'),
            ('UCLA', 'UCLA'),
            ('LMU', 'LMU'),
            ('Pepperdine', 'PEPPERDINE'),
            ('Irvine', 'UC IRVINE'),
            ('San Diego', 'UC SAN DIEGO'),
            ('SMC', "SAINT MARY'S"),
            ('Davis', 'UC DAVIS')
        ]

        # Initialize a list to store all final DataFrames
        all_final_dfs = []

        # Process each sheet
        for sheet_name, school in schools:
            # Load outreach and event data
            outreach_df = pd.read_excel(outreach_file, sheet_name=sheet_name)
            event_df = pd.read_excel(event_file)

            # Standardize Growth Officer names
            outreach_df['Growth Officer'] = outreach_df['Growth Officer'].replace(growth_officer_mapping)

            # Filter for relevant school in the event data
            event_df_filtered = event_df[event_df['Select Your School'].str.strip().str.upper() == school.upper()]

            # Convert date columns to datetime
            outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
            event_df_filtered['Date of the Event'] = pd.to_datetime(event_df_filtered['Date of the Event'], errors='coerce')

            # Drop rows with NaT in date columns
            outreach_df = outreach_df.dropna(subset=['Date'])
            event_df_filtered = event_df_filtered.dropna(subset=['Date of the Event'])

            # Match outreach records with events within a 10-day range
            matched_records = []
            for _, outreach_row in outreach_df.iterrows():
                outreach_date = outreach_row['Date']

                # Find events within 10 days after the outreach date
                matching_events = event_df_filtered[
                    (event_df_filtered['Date of the Event'] >= outreach_date - pd.Timedelta(days=10)) &
                    (event_df_filtered['Date of the Event'] <= outreach_date)
                ]

                if not matching_events.empty:
                    # Combine event details
                    combined_event_name = "/".join(matching_events['Event Name'].unique())
                    combined_event_location = "/".join(matching_events['Location'].unique())
                    combined_event_officer = "/".join(matching_events['Name'].unique())

                    # Create a combined row
                    combined_row = {
                        'Outreach Date': outreach_row['Date'],
                        'Growth Officer': outreach_row.get('Growth Officer', ''),
                        'Outreach Name': outreach_row.get('Name', ''),
                        'Occupation': outreach_row.get('Occupation', ''),
                        'Email': outreach_row.get('Email', ''),
                        'Event Name': combined_event_name,
                        'Event Location': combined_event_location,
                        'Event Officer': combined_event_officer,
                        'Select Your School': "/".join(matching_events['Select Your School'].unique()),
                        'Request type?': "/".join(matching_events['Request type?'].unique()),
                        'Audience': "/".join(matching_events['Audience'].unique())
                    }
                    matched_records.append(combined_row)

            # Convert matched records to DataFrame
            final_df = pd.DataFrame(matched_records)
            all_final_dfs.append(final_df)

        # Combine all DataFrames
        combined_df = pd.concat(all_final_dfs, ignore_index=True)
        return combined_df

    except Exception as e:
        st.error(f"An error occurred during data processing: {e}")
        return pd.DataFrame()

# Submit button and processing
if st.button("Process Files"):
    if not uploaded_outreach or not uploaded_event:
        st.error("Please upload all required files.")
    else:
        # Process the uploaded files
        result_df = process_data(uploaded_outreach, uploaded_event)
        if not result_df.empty:
            st.success("Data processing completed successfully!")
            st.write("Processed Data:")
            st.dataframe(result_df)

            # Download the processed file
            csv = result_df.to_csv(index=False)
            st.download_button(
                label="Download Processed Data as CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv"
            )
        else:
            st.error("No data processed. Please check your input files.")
