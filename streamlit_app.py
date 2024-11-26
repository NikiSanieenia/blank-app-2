import streamlit as st


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
uploaded_outreach = st.file_uploader("Upload Member Outreach File", type=["csv", "xlsx", "xls"])


st.subheader("Event Debrief File")
uploaded_debrief = st.file_uploader("Upload Event Debrief File", type=["csv", "xlsx", "xls"])


st.subheader("Approved Applications File")
uploaded_approved = st.file_uploader("Upload Approved Applications File", type=["csv", "xlsx", "xls"])


st.subheader("Submitted Applications File")
uploaded_submitted = st.file_uploader("Upload Submitted Applications File", type=["csv", "xlsx", "xls"])


# Submit button and validation
if st.button("Upload All Files to Drive"):
   missing_files = []
   if not uploaded_outreach:
       missing_files.append("Member Outreach File")
   if not uploaded_debrief:
       missing_files.append("Event Debrief File")
   if not uploaded_approved:
       missing_files.append("Approved Applications File")
   if not uploaded_submitted:
       missing_files.append("Submitted Applications File")
  
   if missing_files:
       st.error(f"Error: The following files are missing: {', '.join(missing_files)}")
   else:
       st.success("All files have been uploaded successfully!")
       st.write("You can now proceed with the next steps.")
