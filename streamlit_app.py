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

                # Perform a left join based on a 10-day range
                def left_join_with_tolerance(outreach_df, events_df, tolerance_days=10):
                    # Add a key for Cartesian product merge
                    outreach_df['key'] = 1
                    events_df['key'] = 1

                    # Cartesian product merge
                    merged = pd.merge(outreach_df, events_df, on='key').drop(columns=['key'])
                    merged['date_diff'] = (merged['Date of the Event'] - merged['Date']).dt.days

                    # Filter to only include events within the tolerance range
                    merged = merged[(merged['date_diff'] >= 0) & (merged['date_diff'] <= tolerance_days)]

                    # Keep only the closest event for each outreach date
                    closest_events = merged.loc[merged.groupby('Date')['date_diff'].idxmin()]

                    # Perform a left join to retain all outreach records
                    result = pd.merge(outreach_df, closest_events, how='left', on=['Date'], suffixes=('', '_event'))
                    return result

                # Apply the left join
                final_df = left_join_with_tolerance(outreach_df, events_df)

                # Append the processed DataFrame to the list
                all_final_dfs.append(final_df)
                total_rows_individual += len(final_df)

            # Concatenate all DataFrames
            Phase_1 = pd.concat(all_final_dfs, ignore_index=True)

            # Display the processed DataFrame
            st.write("Processed Data:")
            st.dataframe(Phase_1)
            st.success(f"Data processed successfully! Total rows: {len(Phase_1)}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
