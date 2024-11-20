import streamlit as st
import pandas as pd
import io

# Set up the page
st.set_page_config(page_title="UCU Data Processing Tool", layout="centered")

st.title("UCU Data File Upload")
st.write("Upload the required files below to process and analyze the data.")

# Upload files
uploaded_outreach = st.file_uploader("Upload 'Member Outreach File'", type=["csv", "xlsx"])
uploaded_debrief = st.file_uploader("Upload 'Event Debrief File'", type=["csv", "xlsx"])
uploaded_approved = st.file_uploader("Upload 'Approved Applications File'", type=["csv"])
uploaded_submitted = st.file_uploader("Upload 'Submitted Applications File'", type=["csv"])

# Function to run the provided analysis code
def process_files(outreach_file, debrief_file, approved_file, submitted_file):
    try:
        # Read input files into pandas DataFrames
        outreach_df = pd.read_excel(outreach_file) if outreach_file.name.endswith('.xlsx') else pd.read_csv(outreach_file)
        event_df = pd.read_excel(debrief_file) if debrief_file.name.endswith('.xlsx') else pd.read_csv(debrief_file)
        approved_df = pd.read_csv(approved_file)
        submitted_df = pd.read_csv(submitted_file)

        # Your provided Python logic starts here
        all_final_dfs = []
        schools = [
            ('UTA', 'UT ARLINGTON'), ('SCU', 'SANTA CLARA'), ('UCLA', 'UCLA'),
            ('LMU', 'LMU'), ('Pepperdine', 'PEPPERDINE'), ('Irvine', 'UC IRVINE'),
            ('San Diego', 'UC SAN DIEGO'), ('SMC', "SAINT MARY'S"), ('Davis', 'UC DAVIS')
        ]

        growth_officer_mapping = {
            'ileana': 'Ileana Heredia', 'Ileana': 'Ileana Heredia', 'BK': 'Brian Kahmar', 'JR': 'Julia Racioppo',
            'Jordan': 'Jordan Richied', 'VN': 'Veronica Nims', 'vn': 'Veronica Nims',
            'Dom': 'Domenic Noto', 'Megan': 'Megan Sterling', 'Veronica': 'Veronica Nims',
            'SB': 'Sheena Barlow', 'Julio': 'Julio Macias', 'Mo': 'Monisha Donaldson'
        }

        for sheet_name, school in schools:
            # Process each sheet and apply your logic
            outreach_df['Growth Officer'] = outreach_df['Growth Officer'].replace(growth_officer_mapping)
            events_df = event_df[event_df['Select Your School'].str.strip().str.upper() == school.upper()]

            outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
            events_df['Date of the Event'] = pd.to_datetime(events_df['Date of the Event'], errors='coerce')

            matched_records = []
            for _, outreach_row in outreach_df.iterrows():
                outreach_date = outreach_row['Date']
                matching_events = events_df[
                    (events_df['Date of the Event'] >= outreach_date - pd.Timedelta(days=10)) &
                    (events_df['Date of the Event'] <= outreach_date)
                ]

                if not matching_events.empty:
                    combined_event_name = "/".join(matching_events['Event Name'].unique())
                    combined_event_location = "/".join(matching_events['Location'].unique())
                    combined_event_officer = "/".join(matching_events['Name'].unique())

                    combined_row = {
                        'Outreach Date': outreach_row['Date'], 'Growth Officer': outreach_row.get('Growth Officer', ''),
                        'Outreach Name': outreach_row.get('Name', ''), 'Occupation': outreach_row.get('Occupation', ''),
                        'Email': outreach_row.get('Email', ''), 'Date of the Event': outreach_date,
                        'Event Location': combined_event_location, 'Event Name': combined_event_name,
                        'Event Officer': combined_event_officer,
                        'Select Your School': "/".join(matching_events['Select Your School'].unique()),
                        'Request type?': "/".join(matching_events['Request type?'].unique()),
                        'Audience': "/".join(matching_events['Audience'].unique())
                    }
                    matched_records.append(combined_row)

            final_df = pd.DataFrame(matched_records)
            all_final_dfs.append(final_df)

        combined_df = pd.concat(all_final_dfs, ignore_index=True)

        # Phase 2 processing
        joined_approved = combined_df.merge(approved_df, how='left', left_on='Outreach Name', right_on='memberName')
        joined_submitted = joined_approved.merge(submitted_df, how='left', left_on='Outreach Name', right_on='memberName')

        # Dropping duplicates if needed
        combined_data = joined_submitted.drop_duplicates()

        st.success("Data processed successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Run processing if all files are uploaded
if st.button("Run Analysis"):
    if uploaded_outreach and uploaded_debrief and uploaded_approved and uploaded_submitted:
        process_files(uploaded_outreach, uploaded_debrief, uploaded_approved, uploaded_submitted)
    else:
        st.error("Please upload all required files to proceed.")
