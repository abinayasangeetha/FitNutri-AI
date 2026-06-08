from pydantic import BaseModel


class UserProfile(BaseModel):
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str
    goal: str
    diet_preference: str


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str

class CalorieBurnRequest(BaseModel):
    user_id: str
    exercise: str
    minutes: int