import streamlit as st
import requests
from database import (
    create_user,
    get_user,
    hash_password,
    verify_password
)
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="FitNutri AI",
    page_icon="🥗",
    layout="wide"
)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None
st.title("🥗 FitNutri AI")
st.subheader("Personalized Healthcare & Weight Management Assistant")
if not st.session_state.logged_in:

    auth_tab1, auth_tab2 = st.tabs(
        ["Login", "Signup"]
    )

    with auth_tab1:

        st.subheader("Login")

        login_email = st.text_input(
            "Email"
        )

        login_password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            user = get_user(
                login_email
            )

            if user and verify_password(
                login_password,
                user[3]
            ):

                st.session_state.logged_in = True
                st.session_state.user_email = login_email

                st.success(
                    "Login Successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Credentials"
                )

    with auth_tab2:

        st.subheader("Signup")

        signup_name = st.text_input(
            "Name"
        )

        signup_email = st.text_input(
            "Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button("Create Account"):

            try:

                create_user(
                    signup_name,
                    signup_email,
                    hash_password(
                        signup_password
                    )
                )

                st.success(
                    "Account Created"
                )

            except:

                st.error(
                    "Email already exists"
                )

    st.stop()

# ---------------- SIDEBAR ----------------
if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.user_email = None

    st.rerun()
st.sidebar.header("👤 User Profile")
user_id = st.session_state.user_email
st.sidebar.success(
    f"Logged in as: {user_id}"
)
profile_data = None

try:
    response = requests.get(
        f"{API_URL}/profile/{user_id}"
    )

    if response.status_code == 200:
        profile_data = response.json()

except:
    pass

age = st.sidebar.number_input(
    "Age",
    min_value=1,
    max_value=100,
    value=int(
        profile_data["age"]
    ) if profile_data else 21
)

gender_options = [
    "male",
    "female"
]

gender = st.sidebar.selectbox(
    "Gender",
    gender_options,
    index=gender_options.index(
        profile_data["gender"]
    ) if profile_data else 0
)
height = st.sidebar.number_input(
    "Height (cm)",
    value=float(
        profile_data["height_cm"]
    ) if profile_data else 170.0
)

weight = st.sidebar.number_input(
    "Weight (kg)",
    value=float(
        profile_data["weight_kg"]
    ) if profile_data else 70.0
)

activity = st.sidebar.selectbox(
    "Activity Level",
    [
        "sedentary",
        "light",
        "moderate",
        "active",
        "very_active"
    ]
)

goal = st.sidebar.selectbox(
    "Goal",
    [
        "weight loss",
        "weight gain",
        "muscle gain",
        "maintenance"
    ]
)
diet_preference = st.sidebar.selectbox(
    "Diet Preference",
    [
        "Vegetarian",
        "Vegan",
        "Eggetarian",
        "Non-Vegetarian"
    ]
)

if st.sidebar.button("Save Profile"):

    profile_data = {
        "age": age,
        "gender": gender,
        "height_cm": height,
        "weight_kg": weight,
        "activity_level": activity,
        "goal": goal,
        "diet_preference": diet_preference
    }

    response = requests.post(
        f"{API_URL}/profile/{user_id}",
        json=profile_data
    )

    st.sidebar.success("Profile Saved")

# ---------------- METRICS ----------------
st.success(
    "👋 Welcome to FitNutri AI. Get personalized meal plans, workout routines, and health recommendations."
)


# ---------------- TABS ----------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "💬 Chat",
        "🍽 Meal Plan",
        "🏋 Workout",
        "📊 Health Report"
    ]
)

# ---------------- CHAT ----------------

with tab1:

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input(
        "Ask FitNutri AI..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        response = requests.post(
            f"{API_URL}/chat",
            json={
                "user_id": user_id,
                "message": prompt
            }
        )

        data = response.json()

        st.write(data)  # temporary debug

        if "response" in data:
           bot_response = data["response"]
        else:
           st.error(data)
           st.stop()

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": bot_response
            }
        )

        st.rerun()

# ---------------- MEAL PLAN ----------------

with tab2:

    if st.button("Generate Meal Plan"):

        response = requests.get(
            f"{API_URL}/meal-plan/{user_id}"
        )

        st.write(
            response.json()["meal_plan"]
        )

# ---------------- WORKOUT ----------------

with tab3:

    if st.button("Generate Workout Plan"):

        response = requests.get(
            f"{API_URL}/workout-plan/{user_id}"
        )

        st.write(
            response.json()["workout_plan"]
        )

# ---------------- HEALTH REPORT ----------------


with tab4:
    response = requests.get(
    f"{API_URL}/analysis/{user_id}"
    )

    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    analysis = response.json()
    protein = requests.get(
        f"{API_URL}/protein/{user_id}"
    ).json()

    water = requests.get(
        f"{API_URL}/water/{user_id}"
    ).json()

    response = requests.get(
    f"{API_URL}/health-report/{user_id}"
    )
    if response.status_code == 200:

        report = response.json()

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "BMI",
                report["BMI"]
            )

            st.success(
                report["BMI_Category"]
            )

            st.metric(
           "Daily Protein Target",
         f"{protein['protein_required_g_per_day']} g/day"
          )

        with col2:

            st.metric(
               "Daily Calories Needed",
             f"{analysis['MaintenanceCalories']} kcal/day"
            )

            st.metric(
                "Daily Water Target",
             f"{water['recommended_water_liters_per_day']} L/day"
            )

            st.info(
                f"Goal: {report['Goal']}"
            )

        st.divider()
        if report.get("Goal_Warning"):
           st.warning(report["Goal_Warning"])
        st.subheader(
            "🤖 Personalized Recommendations"
        )

        st.markdown(
            report["AI_Recommendation"]
        )