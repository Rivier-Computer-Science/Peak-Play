import os
import requests
from crewai.tools import tool
from pydantic import BaseModel, HttpUrl
from typing import List


UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY')
if not UNSPLASH_API_KEY:
    raise ValueError("UNSPLASH_API_KEY not found in environment variables. Please set it accordingly.")


class UnsplashImage(BaseModel):
    image_url: HttpUrl
    photographer: str


@tool('search_unsplash_images')
def search_unsplash_images(query: str, per_page: int = 5) -> List[UnsplashImage]:
    """
    Searches Unsplash for images based on the provided query.
    Returns a list of images including their URLs and photographer names suitable for commercial websites.
    """
    url = "https://api.unsplash.com/search/photos"
    headers = {"Accept-Version": "v1"}
    params = {
        "client_id": UNSPLASH_API_KEY,
        "query": query,
        "per_page": per_page
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        images = []
        for result in data.get("results", []):
            image_url = result.get("urls", {}).get("regular")
            photographer_name = result.get("user", {}).get("name")
            if image_url and photographer_name:
                images.append(UnsplashImage(image_url=image_url, photographer=photographer_name))
        return images
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
