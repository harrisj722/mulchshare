import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --------------------------------------
# Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('mulchshare_credentials.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet
sheet = client.open("MulchShare_Registrations").sheet1

# --------------------------------------
# Streamlit page settings
st.set_page_config(page_title="MulchShare", layout="centered")

st.title("🌱 MulchShare – Free Mulch Delivered to You!")
st.write("Register your address to receive free mulch from local suppliers.")

# --------------------------------------
# Geocode address function
def geocode_address(address):
    geolocator = Nominatim(user_agent="mulchshare")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# --------------------------------------
# Registration Form
with st.form("register_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    address = st.text_input("Address")
    instructions = st.text_area("Access Instructions")
    pickup = st.radio("Willing to Pick Up Mulch if Needed?", ("Yes", "No"))
    notes = st.text_area("Notes (Optional)")
    submit = st.form_submit_button("Register")

    if submit:
        lat, lon = geocode_address(address)
        if lat and lon:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [timestamp, name, email, phone, address, instructions, pickup, notes]
            sheet.append_row(row)
            st.success("✅ Registration successful! Thanks for joining MulchShare.")
        else:
            st.error("⚠️ Could not locate address. Please check your address and try again.")

# --------------------------------------
# Display Map
st.subheader("📍 Drop-off Locations (Registered Addresses)")

records = sheet.get_all_records()

if records:
    df = pd.DataFrame(records)

    m = folium.Map(location=[-40.9006, 174.8860], zoom_start=6)

    for _, row in df.iterrows():
        try:
            loc = Nominatim(user_agent="mulchshare_map").geocode(row['Address'])
            if loc:
                popup = f"<b>{row['Name']}</b><br>📍 {row['Address']}<br>📞 {row['Phone Number']}"
                folium.Marker(
                    [loc.latitude, loc.longitude],
                    popup=popup,
                    icon=folium.Icon(color="green", icon="truck", prefix="fa")
                ).add_to(m)
        except:
            pass

    st_folium(m, width=700, height=500)
else:
    st.info("No registered addresses yet.")
