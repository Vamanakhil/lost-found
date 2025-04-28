# lost_and_found_app_v2.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from PIL import Image

# --- Setup ---
st.set_page_config(page_title="Lost & Found | College Campus", page_icon="🎒", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🎒 Lost and Found Portal</h1>", unsafe_allow_html=True)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

DB_FILE = "lost_found_db.csv"
if os.path.exists(DB_FILE):
    db = pd.read_csv(DB_FILE)
else:
    db = pd.DataFrame(columns=["Type", "Item Name", "Description", "Location", "Date", "Contact", "Image Path"])

# --- Sidebar Menu ---
st.sidebar.header("📋 Navigation")
menu = st.sidebar.radio("Choose an option", ["🏷 Report Item", "🔍 View Items", "🔎 Search"])

# --- Functions ---

def save_to_database(entry):
    global db
    db = pd.concat([db, pd.DataFrame([entry])], ignore_index=True)
    db.to_csv(DB_FILE, index=False)

def upload_image(file):
    if file:
        filepath = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}")
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        return filepath
    return None

def display_item_card(row):
    col1, col2 = st.columns([1, 2])
    with col1:
        if pd.notna(row['Image Path']):
            st.image(row['Image Path'], width=150)
    with col2:
        st.markdown(f"### {row['Item Name']} {'🛑' if row['Type']=='Lost' else '✅'}")
        st.markdown(f"**Type:** {row['Type']}")
        st.markdown(f"**Location:** {row['Location']}")
        st.markdown(f"**Date:** {row['Date']}")
        st.markdown(f"**Description:** {row['Description']}")
        st.markdown(f"**Contact:** {row['Contact']}")
    st.markdown("---")

# --- Pages ---

if menu == "🏷 Report Item":
    st.subheader("📝 Report a Lost or Found Item")
    
    item_type = st.selectbox("Type", ["Lost", "Found"])
    item_name = st.text_input("Item Name")
    description = st.text_area("Description")
    location = st.text_input("Location where item was lost/found")
    date = st.date_input("Date")
    contact = st.text_input("Your Contact Information (Phone / Email)")
    image = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

    if st.button("Submit"):
        if item_name and description and location and contact:
            image_path = upload_image(image)
            entry = {
                "Type": item_type,
                "Item Name": item_name,
                "Description": description,
                "Location": location,
                "Date": date.strftime("%Y-%m-%d"),
                "Contact": contact,
                "Image Path": image_path
            }
            save_to_database(entry)
            st.success(f"{item_type} item reported successfully!")
        else:
            st.error("Please fill all the required fields!")

elif menu == "🔍 View Items":
    st.subheader("📋 List of Items")
    item_type_filter = st.selectbox("Filter by Type", ["All", "Lost", "Found"])

    if item_type_filter == "All":
        filtered_db = db
    else:
        filtered_db = db[db['Type'] == item_type_filter]

    if filtered_db.empty:
        st.warning("No items reported yet.")
    else:
        for idx, row in filtered_db.iterrows():
            display_item_card(row)

elif menu == "🔎 Search":
    st.subheader("🔍 Search Items")
    keyword = st.text_input("Enter item name, description, or location to search")

    if keyword:
        results = db[
            db["Item Name"].str.contains(keyword, case=False, na=False) |
            db["Description"].str.contains(keyword, case=False, na=False) |
            db["Location"].str.contains(keyword, case=False, na=False)
        ]
        if results.empty:
            st.warning("No matching items found.")
        else:
            for idx, row in results.iterrows():
                display_item_card(row)