def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def calculate_bmr(weight, height_cm, age, gender):

    if gender.lower() == "male":
        return round(
            10 * weight +
            6.25 * height_cm -
            5 * age + 5
        )

    return round(
        10 * weight +
        6.25 * height_cm -
        5 * age - 161
    )


def calculate_daily_calories(bmr, activity_level):

    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    factor = activity_factors.get(
        activity_level.lower(),
        1.2
    )

    return round(bmr * factor)
def calculate_protein(weight):
    return round(weight * 1.6, 2)
def calculate_water_intake(weight):
    return round(weight * 35)
def calories_burned(weight, minutes, met):
    return round(
        (met * 3.5 * weight / 200) * minutes
    )