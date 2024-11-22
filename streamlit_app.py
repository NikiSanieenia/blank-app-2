import pandas as pd
import streamlit as st

# File upload section
st.title("Data Processing for Outreach and Events")

uploaded_outreach_file = st.file_uploader("Upload Outreach Data File (Excel)", type=["xlsx"])
uploaded_event_file = st.file_uploader("Upload Event Data File (Excel)", type=["xlsx"])
uploaded_approved_file = st.file_uploader("Upload Approved Applications File (CSV)", type=["csv"])
uploaded_submitted_file = st.file_uploader("Upload Submitted Applications File (CSV)", type=["csv"])

if uploaded_outreach_file and uploaded_event_file and uploaded_approved_file and uploaded_submitted_file:
    # Load files
    outreach_data = pd.read_excel(uploaded_outreach_file, sheet_name=None)  # Load all sheets
    event_data = pd.read_excel(uploaded_event_file)
    approved_data = pd.read_csv(uploaded_approved_file)
    submitted_data = pd.read_csv(uploaded_submitted_file)

    st.subheader("Loaded Data")
    st.write("Outreach Data Sheets")
    for sheet_name, df in outreach_data.items():
        st.write(f"Sheet: {sheet_name}")
        st.dataframe(df)

    st.write("Event Data")
    st.dataframe(event_data)

    st.write("Approved Memberships")
    st.dataframe(approved_data)

    st.write("Submitted Memberships")
    st.dataframe(submitted_data)

    # Define schools and mapping
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

    all_final_dfs = []

    for sheet_name, school in schools:
        if sheet_name not in outreach_data:
            continue

        outreach_df = outreach_data[sheet_name]
        outreach_df['Growth Officer'] = outreach_df['Growth Officer'].replace(growth_officer_mapping)

        # Filter for relevant school in event data
        event_df = event_data[event_data['Select Your School'].str.strip().str.upper() == school.upper()]

        # Display intermediate tables
        st.write(f"Processing Sheet: {sheet_name}")
        st.write("Outreach Data (Before Cleaning)")
        st.dataframe(outreach_df)

        st.write("Event Data (Filtered by School)")
        st.dataframe(event_df)

        # Date processing and filtering
        outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
        event_df['Date of the Event'] = pd.to_datetime(event_df['Date of the Event'], errors='coerce')
        outreach_df = outreach_df.dropna(subset=['Date'])
        event_df = event_df.dropna(subset=['Date of the Event'])

        matched_records = []
        unmatched_outreach = outreach_df.copy()
        unmatched_event = event_df.copy()

        # Matching outreach and event data
        for _, outreach_row in outreach_df.iterrows():
            outreach_date = outreach_row['Date']
            matching_events = event_df[
                (event_df['Date of the Event'] >= outreach_date - pd.Timedelta(days=10)) &
                (event_df['Date of the Event'] <= outreach_date)
            ]

            if not matching_events.empty:
                combined_event_name = "/".join(matching_events['Event Name'].unique())
                combined_event_location = "/".join(matching_events['Location'].unique())
                combined_event_officer = "/".join(matching_events['Name'].unique())

                matched_records.append({
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
                })

        # Create final DataFrame for this sheet
        final_df = pd.DataFrame(matched_records)
        all_final_dfs.append(final_df)

        st.write(f"Matched Records for {sheet_name}")
        st.dataframe(final_df)

    # Combine all sheets
    Phase_1 = pd.concat(all_final_dfs, ignore_index=True)
    st.subheader("Phase 1 Combined Data")
    st.dataframe(Phase_1)

    # Join with approved memberships
    joined_approved = Phase_1.merge(
        approved_data,
        how='left',
        left_on='Outreach Name',
        right_on='memberName'
    ).drop_duplicates()

    st.subheader("Joined with Approved Memberships")
    st.dataframe(joined_approved)

    matched_approved = joined_approved[joined_approved['memberName'].notna()]

    st.subheader("Matched Approved Data")
    st.dataframe(matched_approved)

    # Join with submitted memberships
    joined_submitted = Phase_1.merge(
        submitted_data,
        how='left',
        left_on='Outreach Name',
        right_on='memberName'
    ).drop_duplicates()

    st.subheader("Joined with Submitted Memberships")
    st.dataframe(joined_submitted)

    matched_submitted = joined_submitted[joined_submitted['memberName'].notna()]

    st.subheader("Matched Submitted Data")
    st.dataframe(matched_submitted)

    # Combine matched data
    final_table = matched_approved.merge(
        matched_submitted,
        how='left',
        on=[col for col in matched_approved.columns if col in matched_submitted.columns]
    ).drop_duplicates()

    st.subheader("Final Table")
    st.dataframe(final_table)

else:
    st.warning("Please upload all required files.")
