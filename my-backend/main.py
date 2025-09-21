from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from starlette.middleware.cors import CORSMiddleware
import json
import os
import uuid

app = FastAPI(title="Career Compass API")

# Allow requests from React frontend
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Placeholder for user database
users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "fakehashedpassword", # In a real app, hash this properly
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

def get_user(username: str):
    if username in users_db:
        return UserInDB(**users_db[username])
    return None

def verify_password(plain_password, hashed_password):
    return plain_password == hashed_password # Placeholder for actual password hashing verification

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_user(token) # Here, for simplicity, token is directly used as username
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

class QuizAnswer(BaseModel):
    question_id: str # Corrected from int to str
    answer: int # Assuming answers are numerical, e.g., 1-5 for a Likert scale

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]

# New models for personality profile and career recommendations
class PersonalityProfile(BaseModel):
    MBTI: str
    OCEAN: dict
    interests: List[str]

class CareerRecommendation(BaseModel):
    career: str
    required_skills: List[str]
    salary: str
    growth_potential: str
    future_trends: List[str]

class CareerTrendItem(BaseModel):
    trend_name: str
    summary: str
    status: str # e.g., "rising", "falling", "stable"
    trend_score: float # e.g., a score from 0 to 1 for impact/relevance

def classify_personality(quiz_answers: QuizSubmission) -> PersonalityProfile:
    # Placeholder for a more sophisticated personality classification logic
    # In a real application, this would involve mapping answers to MBTI and OCEAN scores.
    # For now, we'll return a static profile.
    
    # Simple logic to demonstrate processing:
    # Count positive/negative responses for a very basic "trait" indication
    positive_answers = sum(1 for q in quiz_answers.answers if q.answer > 3) # Assuming 1-5 scale, >3 is positive
    
    if positive_answers > len(quiz_answers.answers) / 2:
        mbti_type = "ESTJ" # Example for a more "positive" leaning
        ocean_traits = {"Openness": 4, "Conscientiousness": 5, "Extraversion": 4, "Agreeableness": 3, "Neuroticism": 2}
        interests_list = ["Technology", "Leadership", "Problem Solving"]
    else:
        mbti_type = "INFP" # Example for a more "introverted/feeling" leaning
        ocean_traits = {"Openness": 3, "Conscientiousness": 3, "Extraversion": 2, "Agreeableness": 4, "Neuroticism": 3}
        interests_list = ["Art", "Writing", "Helping Others"]

    return PersonalityProfile(MBTI=mbti_type, OCEAN=ocean_traits, interests=interests_list)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In a real app, generate a JWT token here
    return {"access_token": user.username, "token_type": "bearer"} # Using username as a mock token

@app.get("/")
async def read_root():
    return {"message": "Welcome to Career Compass API"}

# Mock AI Endpoints (replace with actual AI logic later)
@app.post("/quiz/submit")
async def submit_quiz(quiz_submission: QuizSubmission, current_user: User = Depends(get_current_user)):
    # Use the placeholder personality classifier
    personality_profile = classify_personality(quiz_submission)
    return {"message": "Quiz submitted successfully", "profile": personality_profile.dict(), "user": current_user.username}

@app.get("/careers/recommend")
async def get_career_recommendations(profile: PersonalityProfile, current_user: User = Depends(get_current_user)):
    # Placeholder for career recommendation engine
    # In a real application, this would use the profile to generate relevant recommendations.
    # For now, we'll return static recommendations based on generic profiles.

    recommendations = [
        CareerRecommendation(
            career="AI Engineer",
            required_skills=["Python", "Machine Learning", "Deep Learning", "Cloud Platforms"],
            salary="$120,000 - $180,000",
            growth_potential="High",
            future_trends=["Generative AI", "Ethical AI", "AI in Healthcare"]
        ),
        CareerRecommendation(
            career="Data Scientist",
            required_skills=["Python/R", "Statistics", "Data Visualization", "SQL"],
            salary="$110,000 - $170,000",
            growth_potential="High",
            future_trends=["Big Data Analytics", "Predictive Modeling", "Data Governance"]
        ),
        CareerRecommendation(
            career="UX Designer",
            required_skills=["UI/UX Principles", "Wireframing", "Prototyping", "User Research"],
            salary="$80,000 - $130,000",
            growth_potential="Medium-High",
            future_trends=["AI in UX", "Voice User Interfaces (VUI)", "Inclusive Design"]
        )
    ]
    return {"recommendations": [r.dict() for r in recommendations], "user": current_user.username}

@app.get("/careers/trends")
async def get_career_trends(current_user: User = Depends(get_current_user)) -> List[CareerTrendItem]:
    # Placeholder for career trend scanning and summarization
    # In a real application, this would involve scanning various sources (research papers, job boards, blogs)
    # and using AI to identify and categorize trends.

    trends = [
        CareerTrendItem(
            trend_name="AI Ethics Specialist",
            summary="Growing demand for ethical considerations in AI development.",
            status="rising",
            trend_score=0.95
        ),
        CareerTrendItem(
            trend_name="Green Energy Consultant",
            summary="Increasing focus on sustainable energy solutions.",
            status="rising",
            trend_score=0.88
        ),
        CareerTrendItem(
            trend_name="Blockchain Developer",
            summary="Continued, but more specialized, demand in decentralized technologies.",
            status="stable",
            trend_score=0.75
        ),
        CareerTrendItem(
            trend_name="Traditional Retail Manager",
            summary="Facing challenges due to e-commerce growth and automation.",
            status="falling",
            trend_score=0.30
        )
    ]
    return trends

@app.post("/simulation/generate")
async def generate_simulation(current_user: User = Depends(get_current_user)):
    # Placeholder for workplace simulation
    scenario = {
        "description": "You are leading a project to develop a new AI-powered recommendation system. A critical deadline is approaching, and your team is facing unexpected technical challenges.",
        "micro_opportunities": [
            {"opportunity": "Delegating tasks effectively to team members.", "action": "Delegate specific sub-tasks to optimize workflow."},
            {"opportunity": "Communicating with stakeholders about potential delays.", "action": "Prepare a concise update for stakeholders outlining challenges and revised timeline."},
        ]
    }
    return {"scenario": scenario, "user": current_user.username}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load mock data from combined_mock_data.json
COMBINED_MOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), "combined_mock_data.json")
try:
    with open(COMBINED_MOCK_DATA_FILE, "r") as f:
        combined_mock_data = json.load(f)
except FileNotFoundError:
    combined_mock_data = {}
    print(f"Warning: {COMBINED_MOCK_DATA_FILE} not found. Mock data is empty.")

@app.get("/api/trends")
async def get_career_trends(career: str, metric: str):
    career_data = combined_mock_data.get(career)
    if not career_data:
        raise HTTPException(status_code=404, detail="Career not found")

    trends_data = career_data.get("trends", {}).get(metric)
    if not trends_data:
        raise HTTPException(status_code=404, detail=f"Metric {metric} not found for this career")

    insight = f"This is a mock insight for {career} {metric} trends. Gemini integration will fill missing data and provide real insights here later."

    return {"data": trends_data, "insight": insight}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Career Trends API"}


class Event(BaseModel):
    time: str
    title: str
    description: str
    visual_prompt: str
    media_type: str
    media_url: str = ""

class TimelineResponse(BaseModel):
    session_id: str
    person_id: str
    timeline: List[Event]

@app.get("/simulate", response_model=TimelineResponse)
def simulate_career(person_id: str, scenario_params: Dict[str, Any] = None):
    # Use 'combined_mock_data.json' for the simulation data
    persona = combined_mock_data.get(person_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    timeline_events = []
    session_id = str(uuid.uuid4())

    for event_template in persona.get("events_template", []):
        # Placeholder for Vertex AI Generative Media and Cloud Storage upload
        # In a real implementation, you would call Vertex AI here to generate media
        # and then upload it to Cloud Storage, getting a media_url.
        media_url = event_template.get("media_url", "") # Use media_url from template or default to empty

        timeline_events.append(Event(
            time=event_template["time"],
            title=event_template["title"],
            description=event_template["description"],
            visual_prompt=event_template["visual_prompt"],
            media_type=event_template["media_type"],
            media_url=media_url
        ))

    return TimelineResponse(
        session_id=session_id,
        person_id=person_id,
        timeline=timeline_events
    )
