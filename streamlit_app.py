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

    # Growth Officer mapping
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

        event_df = event_data[event_data['Select Your School'].str.strip().str.upper() == school.upper()]
        outreach_df['Date'] = pd.to_datetime(outreach_df['Date'], errors='coerce')
        event_df['Date of the Event'] = pd.to_datetime(event_df['Date of the Event'], errors='coerce')

        outreach_df = outreach_df.dropna(subset=['Date'])
        event_df = event_df.dropna(subset=['Date of the Event'])

        matched_records = []

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

        final_df = pd.DataFrame(matched_records)
        all_final_dfs.append(final_df)

    Phase_1 = pd.concat(all_final_dfs, ignore_index=True)

    # Join with approved and submitted data
    joined_approved = Phase_1.merge(
        approved_data,
        how='left',
        left_on='Outreach Name',
        right_on='memberName'
    ).drop_duplicates()

    matched_approved = joined_approved[joined_approved['memberName'].notna()]

    joined_submitted = Phase_1.merge(
        submitted_data,
        how='left',
        left_on='Outreach Name',
        right_on='memberName'
    ).drop_duplicates()

    matched_submitted = joined_submitted[joined_submitted['memberName'].notna()]

    final_table = matched_approved.merge(
        matched_submitted,
        how='left',
        on=[col for col in matched_approved.columns if col in matched_submitted.columns]
    ).drop_duplicates()

    # Display the final table
    st.write("Final Table")
    st.dataframe(final_table)

else:
    st.warning("Please upload all required files.")
