import streamlit as st
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Page setup
st.set_page_config(page_title="Mulch Share", layout="wide")

# Constants
ACCESS_CODE = "mulch2025"

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)
sheet = client.open("MulchShare_Registrations").sheet1

# Landing Page Description
st.markdown("""
## 🌱 Welcome to Mulch Share

**Mulch Share** connects:
- 🏡 Residents who want free mulch
- 🚛 Contractors with mulch to drop off (saving disposal costs)

---

### How It Works
1. Residents register their address using the form below.
2. Contractors view a teaser map of interested recipients.
3. With a passcode (provided manually), they can unlock full drop-off info.

---
""")

# Navigation Toggle
view = st.selectbox("Choose your view", ["Register to Receive Mulch", "View Drop-Off Locations"])

# View 1: Registration Form
if view == "Register to Receive Mulch":
    st.subheader("📋 Register to Receive Mulch")

    with st.form("registration_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        address = st.text_input("Delivery Address")
        instructions = st.text_area("Drop-off Instructions (access, gate codes, etc.)")
        submitted = st.form_submit_button("Register")

        if submitted:
            if name and email and phone and address:
                sheet.append_row([name, email, phone, address, instructions])
                st.success("✅ Registration submitted!")
            else:
                st.warning("Please fill in all required fields.")

# View 2: Supplier Map View
else:
    st.subheader("🚛 Drop-Off: View Mulch Recipient Locations")

    password_input = st.text_input("Enter access code to view full details", type="password")
    unlocked = password_input == ACCESS_CODE

    records = sheet.get_all_records()
    if not records:
        st.info("No mulch drop-off registrations yet.")
    else:
        geolocator = Nominatim(user_agent="mulchshare-app")
        map_center = [-40.9, 174.8]  # Center on NZ

        m = folium.Map(location=map_center, zoom_start=5)

        for row in records:
            location = geolocator.geocode(row["Address"])
            if location:
                if unlocked:
                    popup = f"{row['Name']}<br>{row['Email']}<br>{row['Phone']}<br>{row['Drop-off Instructions']}"
                else:
                    popup = "🔒 Registered Recipient (details hidden)"
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup=popup,
                    icon=folium.Icon(color="green", icon="leaf" if unlocked else "info-sign"),
                ).add_to(m)

        st_folium(m, width=800, height=500)
        if not unlocked:
            st.info("Enter the access code above to unlock full details.")
