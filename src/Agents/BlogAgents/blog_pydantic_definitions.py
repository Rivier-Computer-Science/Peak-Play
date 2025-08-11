from typing import List
import pydantic as pydantic

class BlogSportAndTopic(pydantic.BaseModel):
    sport: str
    topic: str

class BlogPostResult(pydantic.BaseModel):
    post_title: str
    post_content: str
    sport: str
    post_tags: List[str]

class BlogPostOutput(pydantic.BaseModel):
    success: str
    result: BlogPostResult
    change_log: List[str]