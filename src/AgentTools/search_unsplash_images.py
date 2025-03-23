import os
import requests
from crewai.tools import tool


UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY')
if not UNSPLASH_API_KEY:
    raise ValueError("UNSPLASH_API_KEY not found in environment variables. Please set it accordingly.")


@tool('search_unsplash_images')
def search_unsplash_images(query: str, per_page: int = 5) -> list:
    """
    Searches Unsplash for images based on the provided query.
    Returns a list of image URLs suitable for commercial websites.
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
        # Extract a simplified list of image URLs (using the 'regular' size)
        image_urls = []
        for result in data.get("results", []):
            url = result.get("urls", {}).get("regular")
            if url:
                image_urls.append(url)
        return image_urls
    else:
        # Return an error message if the API call fails
        return [f"Error: {response.status_code} - {response.text}"]



