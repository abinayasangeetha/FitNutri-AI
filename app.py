from fastapi import FastAPI, HTTPException
from database import (
    create_tables,
    save_message,
    get_messages,
    save_profile_db,
    get_profile_db
)
from models import (
    UserProfile,
    ChatRequest,
    CalorieBurnRequest
)
from user_memory import (
    save_profile,
    get_profile,
    add_message,
    get_history
)
from calculations import (
    calculate_bmi,
    bmi_category,
    calculate_bmr,
    calculate_daily_calories,
    calculate_protein,
    calculate_water_intake,
    calories_burned
)

from chatbot import generate_response

app = FastAPI(
    title="FitNutri AI"
)
create_tables()


@app.get("/")
def home():
    return {
        "message": "FitNutri AI API Running Successfully"
    }


@app.post("/profile/{user_id}")
def create_profile(user_id: str, profile: UserProfile):

    save_profile_db(
        user_id,
        profile.dict()
    )

    return {
        "message": "Profile saved successfully in database"
    }

@app.get("/analysis/{user_id}")
def health_analysis(user_id: str):

    profile = get_profile_db(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    bmi = calculate_bmi(
        profile["weight_kg"],
        profile["height_cm"]
    )

    category = bmi_category(bmi)

    bmr = calculate_bmr(
        profile["weight_kg"],
        profile["height_cm"],
        profile["age"],
        profile["gender"]
    )

    maintenance_calories = calculate_daily_calories(
        bmr,
        profile["activity_level"]
    )

    weight_loss_calories = maintenance_calories - 500

    return {
        "BMI": bmi,
        "Category": category,
        "BMR": bmr,
        "MaintenanceCalories": maintenance_calories,
        "WeightLossCalories": weight_loss_calories
    }

@app.post("/chat")
def chat(chat_request: ChatRequest):

    profile = get_profile_db(chat_request.user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Please create profile first."
        )

    bmi = calculate_bmi(
        profile["weight_kg"],
        profile["height_cm"]
    )

    bmr = calculate_bmr(
        profile["weight_kg"],
        profile["height_cm"],
        profile["age"],
        profile["gender"]
    )

    calories = calculate_daily_calories(
        bmr,
        profile["activity_level"]
    )

    context = f"""
    User Details:
    Age: {profile['age']}
    Gender: {profile['gender']}
    Height: {profile['height_cm']} cm
    Weight: {profile['weight_kg']} kg
    Goal: {profile['goal']}
    Diet Preference: {profile['diet_preference']}
    BMI: {bmi}
    Daily Calories: {calories}
    """

    # Load previous conversations from SQLite
    history = get_messages(
        chat_request.user_id
    )

    response = generate_response(
        chat_request.message,
        context,
        history
    )

    save_message(
        chat_request.user_id,
        "user",
        chat_request.message
    )

    save_message(
        chat_request.user_id,
        "assistant",
        response
    )

    return {
        "response": response
    }
@app.get("/history/{user_id}")
def history(user_id: str):
    return get_history(user_id)

@app.get("/protein/{user_id}")
def protein_requirement(user_id: str):

    profile = get_profile_db(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    protein = calculate_protein(
        profile["weight_kg"]
    )

    return {
        "weight": profile["weight_kg"],
        "protein_required_g_per_day": protein
    }

@app.get("/water/{user_id}")
def water_requirement(user_id: str):

    profile = get_profile_db(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    water = calculate_water_intake(
        profile["weight_kg"]
    )

    return {
        "weight": profile["weight_kg"],
        "recommended_water_ml_per_day": water,
        "recommended_water_liters_per_day": round(water / 1000, 2)
    }
@app.get("/meal-plan/{user_id}")
def meal_plan(user_id: str):

    profile = get_profile_db(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    bmi = calculate_bmi(
        profile["weight_kg"],
        profile["height_cm"]
    )

    diet_rules = ""

    if profile["diet_preference"].lower() == "vegetarian":

        diet_rules = """
        IMPORTANT DIET RULES:

        User is STRICTLY VEGETARIAN.

        NEVER suggest:
        - Chicken
        - Fish
        - Mutton
        - Beef
        - Eggs
        - Seafood

        Use only:
        - Paneer
        - Tofu
        - Soy chunks
        - Lentils
        - Beans
        - Milk
        - Curd
        - Nuts
        - Seeds

        Violation of these rules is not allowed.
        """

    elif profile["diet_preference"].lower() == "vegan":

        diet_rules = """
        IMPORTANT DIET RULES:

        User is VEGAN.

        NEVER suggest:
        - Milk
        - Curd
        - Paneer
        - Cheese
        - Eggs
        - Chicken
        - Fish
        - Any animal product

        Use only plant-based foods.
        """

    prompt = f"""
    You are an expert nutritionist.

    Create a detailed 1-day meal plan.

    User Details:

    Age: {profile['age']}
    Gender: {profile['gender']}
    Weight: {profile['weight_kg']} kg
    Height: {profile['height_cm']} cm
    BMI: {bmi}
    Goal: {profile['goal']}
    Diet Preference: {profile['diet_preference']}

    {diet_rules}

    Include:

    1. Breakfast
    2. Mid-Morning Snack
    3. Lunch
    4. Evening Snack
    5. Dinner

    Mention approximate calories.

    If goal is weight loss:
    - Create calorie deficit meals.

    If goal is weight gain:
    - Create calorie surplus meals.

    If goal is muscle gain:
    - Include high protein foods.

    Rules:
    - Follow diet preference strictly.
    - Use practical foods.
    - Keep the plan easy to follow.
    - Do not violate diet restrictions.
    """

    response = generate_response(
        prompt,
        ""
    )

    return {
        "meal_plan": response
    }

@app.get("/workout-plan/{user_id}")
def workout_plan(user_id: str):

    profile = get_profile_db(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    bmi = calculate_bmi(
        profile["weight_kg"],
        profile["height_cm"]
    )

    prompt = f"""
    Create a personalized weekly workout plan.

    User Details:
    Age: {profile['age']}
    Gender: {profile['gender']}
    Weight: {profile['weight_kg']} kg
    Height: {profile['height_cm']} cm
    BMI: {bmi}
    Goal: {profile['goal']}
    Activity Level: {profile['activity_level']}

    Requirements:

    - Create a 7-day workout plan
    - Mention sets and reps
    - Suggest home workouts
    - No gym equipment required
    - Beginner friendly

    If goal is weight loss:
    Focus on calorie burning.

    If goal is muscle gain:
    Focus on strength training.

    If goal is weight gain:
    Focus on muscle building and moderate cardio.

    Include rest days.
    """
    response = generate_response(
    prompt,
    ""
)   

    return {
        "workout_plan": response
    }

@app.post("/calories-burned")
def calorie_burn(request: CalorieBurnRequest):

    profile = get_profile_db(request.user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    met_values = {
        "walking": 3.5,
        "running": 8,
        "cycling": 7,
        "jump_rope": 12,
        "yoga": 3,
        "stairs": 8.8
    }

    exercise = request.exercise.lower()

    if exercise not in met_values:
        raise HTTPException(
            status_code=400,
            detail="Exercise not supported"
        )

    calories = calories_burned(
        profile["weight_kg"],
        request.minutes,
        met_values[exercise]
    )

    return {
        "exercise": exercise,
        "minutes": request.minutes,
        "estimated_calories_burned": calories
    }

@app.get("/health-report/{user_id}")
def health_report(user_id: str):

    profile = get_profile_db(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    bmi = calculate_bmi(
        profile["weight_kg"],
        profile["height_cm"]
    )

    category = bmi_category(bmi)

    bmr = calculate_bmr(
        profile["weight_kg"],
        profile["height_cm"],
        profile["age"],
        profile["gender"]
    )

    calories = calculate_daily_calories(
        bmr,
        profile["activity_level"]
    )

    protein = calculate_protein(
        profile["weight_kg"]
    )

    water = calculate_water_intake(
        profile["weight_kg"]
    )

    prompt = f"""
You are a professional nutrition and fitness coach.

User Details:

Age: {profile['age']}
Gender: {profile['gender']}
Weight: {profile['weight_kg']} kg
Height: {profile['height_cm']} cm

BMI: {bmi}
BMI Category: {category}

Daily Calories: {calories}
Protein Requirement: {protein} g/day
Water Requirement: {water} ml/day

Goal: {profile['goal']}
Diet Preference: {profile['diet_preference']}
Provide:

1. One short health summary.
2. Top 5 actionable recommendations.
3. One warning if BMI is unhealthy.

Rules:
- Use bullet points.
- Keep response under 120 words.
- No long paragraphs.
- No disclaimer.
- Make it easy for non-technical users.
    """
    warning = ""

    goal = profile["goal"].lower().replace(" ", "")

    if bmi < 18.5 and goal == "weightloss":

       warning = """
       ⚠ Goal Mismatch Detected

Your BMI indicates that you are underweight.

Weight loss may not be appropriate at this time.

Consider weight gain or maintenance instead.
"""
    recommendation = generate_response(
        prompt,
        ""
    )
    
    return {
    "BMI": bmi,
    "BMI_Category": category,
    "BMR": bmr,
    "Daily_Calories": calories,
    "Protein_g": protein,
    "Water_ml": water,
    "Goal": profile["goal"],
    "Goal_Warning": warning,
    "AI_Recommendation": recommendation
    } 
@app.get("/db-history/{user_id}")
def db_history(user_id: str):
    return get_messages(user_id)

@app.get("/profile/{user_id}")
def get_user_profile(user_id: str):

    profile = get_profile_db(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile