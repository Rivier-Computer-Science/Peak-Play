from pydantic import BaseModel
class UpdateProgramData(BaseModel):
    athlete_name: str
    sex: str
    athlete_age: str
    height: str
    weight: str
    primary_sport: str
    primary_sport_level: str
    primary_sport_position: str
    secondary_sport: str
    unique_aspect: str
    overall_performance: int
    difficulty: int
    fatigue: int
    injuries: str
    injury_details: str
    motivation_level: int
    additional_comments: str    





