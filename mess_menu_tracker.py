import streamlit as st
from PIL import Image
from datetime import datetime
import json
import os
import base64
import pyttsx3

# JSON file for user data
USER_FILE = "users.json"

# Global menu and date
menu_data = {
    "Monday": {"Breakfast": "Poha + Tea", "Lunch": "Rajma Chawal", "Dinner": "Roti + Aloo Matar"},
    "Tuesday": {"Breakfast": "Upma", "Lunch": "Kadhi Chawal", "Dinner": "Roti + Mix Veg"},
    "Wednesday": {"Breakfast": "Idli Sambhar", "Lunch": "Chole Bhature", "Dinner": "Paneer + Roti"},
    "Thursday": {"Breakfast": "Bread Butter", "Lunch": "Dal Tadka", "Dinner": "Poori + Aloo"},
    "Friday": {"Breakfast": "Aloo Paratha", "Lunch": "Kadhi Pakoda", "Dinner": "Veg Biryani"},
    "Saturday": {"Breakfast": "Chole Kulche", "Lunch": "Fried Rice", "Dinner": "Khichdi"},
    "Sunday": {"Breakfast": "Halwa Puri", "Lunch": "Special Thali", "Dinner": "Pulao"},
}
today_day = datetime.now().strftime("%A")

# Load/save user data
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

user_db = load_users()
allowed_domain = "vgu.ac.in"

def is_valid_email(email):
    return email.endswith(allowed_domain)

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode()

def decode_image(image_str):
    return base64.b64decode(image_str)

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def show_menu(selected_day):
    st.title("🍽 College Mess Menu Tracker")

    col1, col2 = st.columns([4, 1])
    with col2:
        st.markdown(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

    st.subheader(f"📋 Menu for {selected_day}")
    st.write(f"🍳 Breakfast: {menu_data[selected_day]['Breakfast']}")
    st.write(f"🥗 Lunch: {menu_data[selected_day]['Lunch']}")
    st.write(f"🍽 Dinner: {menu_data[selected_day]['Dinner']}")

    speak_text(f"Today's menu is {selected_day}. Breakfast: {menu_data[selected_day]['Breakfast']}, Lunch: {menu_data[selected_day]['Lunch']}, Dinner: {menu_data[selected_day]['Dinner']}")

    if st.checkbox("📅 Show Weekly Menu"):
        st.subheader("📅 Weekly Menu Overview")
        for day, meals in menu_data.items():
            st.markdown(f"### {day}")
            st.write(f"🍳 Breakfast: {meals['Breakfast']}")
            st.write(f"🥗 Lunch: {meals['Lunch']}")
            st.write(f"🍽 Dinner: {meals['Dinner']}")
            st.markdown("---")

    st.markdown("---")
    st.subheader("⭐ Today's Food Review")
    rating = st.slider("Rate Today's Food", 1, 5, 3)
    comment = st.text_area("Write a review (optional)")
    if st.button("Submit Review"):
        st.success("✅ Thank you for your feedback!")
        speak_text("Thank you for your feedback!")

# Session state init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login/Signup UI
if not st.session_state.logged_in:
    st.title("🔐 Welcome to Mess Portal")
    auth_choice = st.radio("Select Action:", ["Login", "Sign Up"])

    if auth_choice == "Login":
        st.subheader("🔐 Login")
        login_email = st.text_input("College Email")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_email in user_db and user_db[login_email]["password"] == login_password:
                st.session_state.logged_in = True
                st.session_state.user_email = login_email
                st.success("✅ Login Successful!")
                speak_text("Login successful. Welcome to the mess portal")
                st.rerun()
            else:
                st.error("❌ Invalid email or password")

    elif auth_choice == "Sign Up":
        st.subheader("📝 Sign Up")
        name = st.text_input("Full Name")
        enroll = st.text_input("Enrollment Number")
        mobile = st.text_input("Mobile Number")
        signup_email = st.text_input("College Email ID")
        pass1 = st.text_input("Enter Password", type="password")
        pass2 = st.text_input("Re-enter Password", type="password")
        profile_pic = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"])

        if st.button("Submit"):
            if signup_email in user_db:
                st.warning("⚠ Email already registered.")
            elif not is_valid_email(signup_email):
                st.error("❌ Only college domain emails allowed.")
            elif pass1 != pass2:
                st.error("❌ Passwords do not match.")
            else:
                image_str = encode_image(profile_pic) if profile_pic else ""
                user_db[signup_email] = {
                    "password": pass1,
                    "name": name,
                    "enroll": enroll,
                    "mobile": mobile,
                    "profile_pic": image_str
                }
                save_users(user_db)
                st.success("✅ Account created successfully. Please login.")
                speak_text("Account created successfully. Please login")

# After login
else:
    user_info = user_db.get(st.session_state.user_email, {})

    with st.sidebar:
        if user_info.get("profile_pic"):
            st.image(decode_image(user_info["profile_pic"]), width=100)

        # Editable user info
        user_info["name"] = st.text_input("👤 Name", value=user_info.get("name", ""))
        user_info["enroll"] = st.text_input("🆔 Enrollment", value=user_info.get("enroll", ""))
        user_info["mobile"] = st.text_input("📱 Mobile", value=user_info.get("mobile", ""))

        # Save edits
        if st.button("💾 Save Changes"):
            user_db[st.session_state.user_email].update(user_info)
            save_users(user_db)
            st.success("✅ Profile updated")
            speak_text("Profile updated")


        # Day Selection just below user info
        selected_day = st.selectbox("📆 Select Day", list(menu_data.keys()), index=list(menu_data.keys()).index(today_day))

        for _ in range(10):
            st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Show menu now
    show_menu(selected_day)