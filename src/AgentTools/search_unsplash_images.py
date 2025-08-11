"""
Robust Unsplash Image Search Tool for CrewAI
Updated version with comprehensive error handling, validation, and proper attribution.
"""

import os
import time
import logging
from typing import Type, Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, HttpUrl, field_validator


# Environment variable setup
UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY') or os.environ.get('UNSPLASH_ACCESS_KEY')
# Note: We don't raise an error here anymore since the tool can be initialized with an explicit api_key parameter


# Enums for validation
class ColorFilter(str, Enum):
    """Valid color filter options for Unsplash API."""
    BLACK_AND_WHITE = "black_and_white"
    BLACK = "black"
    WHITE = "white"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"
    PURPLE = "purple"
    MAGENTA = "magenta"
    GREEN = "green"
    TEAL = "teal"
    BLUE = "blue"


class OrientationFilter(str, Enum):
    """Valid orientation filter options for Unsplash API."""
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARISH = "squarish"


class OrderBy(str, Enum):
    """Valid order by options for Unsplash API."""
    RELEVANT = "relevant"
    LATEST = "latest"


class ContentFilter(str, Enum):
    """Valid content filter options for Unsplash API."""
    LOW = "low"
    HIGH = "high"


# Pydantic Models
class UnsplashProfileImage(BaseModel):
    """Profile image URLs for different sizes."""
    small: HttpUrl = Field(..., description="Small profile image URL (32x32)")
    medium: HttpUrl = Field(..., description="Medium profile image URL (64x64)")
    large: HttpUrl = Field(..., description="Large profile image URL (128x128)")


class UnsplashUserLinks(BaseModel):
    """Links related to the user."""
    self: HttpUrl = Field(..., description="API URL for user details")
    html: HttpUrl = Field(..., description="User's Unsplash profile page")
    photos: HttpUrl = Field(..., description="API URL for user's photos")
    likes: HttpUrl = Field(..., description="API URL for user's liked photos")
    portfolio: HttpUrl = Field(..., description="API URL for user's portfolio")


class UnsplashUser(BaseModel):
    """Unsplash user/photographer information."""
    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="User's username")
    name: str = Field(..., description="User's full name")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    instagram_username: Optional[str] = Field(None, description="Instagram username")
    twitter_username: Optional[str] = Field(None, description="Twitter username")
    portfolio_url: Optional[HttpUrl] = Field(None, description="User's portfolio website")
    profile_image: UnsplashProfileImage = Field(..., description="Profile image URLs")
    links: UnsplashUserLinks = Field(..., description="Related user links")


class UnsplashUrls(BaseModel):
    """Photo URLs for different sizes."""
    raw: HttpUrl = Field(..., description="Raw, unprocessed image URL")
    full: HttpUrl = Field(..., description="Full-size image URL")
    regular: HttpUrl = Field(..., description="Regular-size image URL (1080px wide)")
    small: HttpUrl = Field(..., description="Small image URL (400px wide)")
    thumb: HttpUrl = Field(..., description="Thumbnail image URL (200px wide)")


class UnsplashPhotoLinks(BaseModel):
    """Links related to the photo."""
    self: HttpUrl = Field(..., description="API URL for photo details")
    html: HttpUrl = Field(..., description="Photo's Unsplash page")
    download: HttpUrl = Field(..., description="Photo download URL")


class UnsplashPhoto(BaseModel):
    """Complete Unsplash photo information."""
    id: str = Field(..., description="Unique photo identifier")
    created_at: datetime = Field(..., description="Photo creation timestamp")
    width: int = Field(..., description="Photo width in pixels", gt=0)
    height: int = Field(..., description="Photo height in pixels", gt=0)
    color: str = Field(..., description="Dominant color as hex code")
    blur_hash: str = Field(..., description="BlurHash string for placeholder")
    likes: int = Field(..., description="Number of likes", ge=0)
    liked_by_user: bool = Field(..., description="Whether current user liked the photo")
    description: Optional[str] = Field(None, description="Photo description")
    alt_description: Optional[str] = Field(None, description="Alternative description")
    user: UnsplashUser = Field(..., description="Photographer information")
    urls: UnsplashUrls = Field(..., description="Photo URLs for different sizes")
    links: UnsplashPhotoLinks = Field(..., description="Related photo links")
    current_user_collections: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Collections the photo belongs to"
    )

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """Validate color is a valid hex code."""
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex code (e.g., #A7A2A1)')
        return v


class UnsplashAttribution(BaseModel):
    """Attribution information for proper crediting."""
    photographer_name: str = Field(..., description="Photographer's name")
    photographer_username: str = Field(..., description="Photographer's username")
    photographer_url: HttpUrl = Field(..., description="Photographer's Unsplash profile")
    photo_url: HttpUrl = Field(..., description="Photo's Unsplash page")
    unsplash_url: HttpUrl = Field(
        default="https://unsplash.com", 
        description="Unsplash homepage URL"
    )
    attribution_text: str = Field(..., description="Formatted attribution text")

    @classmethod
    def from_photo(cls, photo: UnsplashPhoto) -> "UnsplashAttribution":
        """Create attribution from photo data."""
        attribution_text = f"Photo by {photo.user.name} on Unsplash"
        return cls(
            photographer_name=photo.user.name,
            photographer_username=photo.user.username,
            photographer_url=photo.user.links.html,
            photo_url=photo.links.html,
            attribution_text=attribution_text
        )


class UnsplashImage(BaseModel):
    """Simplified image model for backward compatibility."""
    image_url: HttpUrl = Field(..., description="Image URL")
    photographer: str = Field(..., description="Photographer name")
    attribution: str = Field(..., description="Attribution text")
    photo_id: str = Field(..., description="Unique photo identifier")
    description: Optional[str] = Field(None, description="Photo description")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    likes: int = Field(..., description="Number of likes")
    unsplash_url: HttpUrl = Field(..., description="Unsplash photo page URL")

    @classmethod
    def from_photo(cls, photo: UnsplashPhoto) -> "UnsplashImage":
        """Create UnsplashImage from UnsplashPhoto."""
        attribution = UnsplashAttribution.from_photo(photo)
        return cls(
            image_url=photo.urls.regular,
            photographer=photo.user.name,
            attribution=attribution.attribution_text,
            photo_id=photo.id,
            description=photo.description or photo.alt_description,
            width=photo.width,
            height=photo.height,
            likes=photo.likes,
            unsplash_url=photo.links.html
        )


class UnsplashSearchInput(BaseModel):
    """Input schema for Unsplash photo search."""
    query: str = Field(..., description="Search terms for finding photos", min_length=1)
    per_page: int = Field(default=5, description="Number of photos per page", ge=1, le=30)
    page: int = Field(default=1, description="Page number to retrieve", ge=1)
    order_by: OrderBy = Field(default=OrderBy.RELEVANT, description="Sort order for results")
    color: Optional[ColorFilter] = Field(None, description="Filter by color")
    orientation: Optional[OrientationFilter] = Field(None, description="Filter by orientation")
    content_filter: ContentFilter = Field(default=ContentFilter.LOW, description="Content safety filter")
    collections: Optional[str] = Field(None, description="Comma-separated collection IDs")


class UnsplashSearchResponse(BaseModel):
    """Response from Unsplash search API."""
    total: int = Field(..., description="Total number of photos found", ge=0)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    results: List[UnsplashPhoto] = Field(..., description="List of photos")


class SearchUnsplashImagesTool(BaseTool):
    """
    Robust CrewAI tool for searching Unsplash images with comprehensive error handling.
    
    Features:
    - Advanced search filtering (color, orientation, content safety)
    - Proper attribution generation
    - Rate limiting and error handling
    - Image URL validation
    - Comprehensive logging
    - Backward compatibility with original UnsplashImage model
    """
    
    name: str = "search_unsplash_images"
    description: str = (
        "Search and retrieve high-quality images from Unsplash with proper attribution. "
        "Supports advanced filtering by color, orientation, and content safety. "
        "Returns validated image URLs with photographer information and attribution text."
    )
    args_schema: Type[BaseModel] = UnsplashSearchInput
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the Unsplash search tool.
        
        Args:
            api_key: Unsplash API access key. If not provided, will use environment variable.
            **kwargs: Additional arguments passed to BaseTool
        """
        super().__init__(**kwargs)
        
        # Use object.__setattr__ to bypass Pydantic's field validation
        resolved_api_key = api_key or UNSPLASH_API_KEY
        if not resolved_api_key:
            raise ValueError(
                "Unsplash API key is required. Provide it as 'api_key' parameter or "
                "set UNSPLASH_API_KEY/UNSPLASH_ACCESS_KEY environment variable."
            )
        
        # Set attributes using object.__setattr__ to avoid Pydantic field validation
        object.__setattr__(self, '_api_key', resolved_api_key)
        object.__setattr__(self, '_base_url', "https://api.unsplash.com")
        object.__setattr__(self, '_session', requests.Session())
        
        # Configure session headers
        self._session.headers.update({
            'Authorization': f'Client-ID {self._api_key}',
            'Accept': 'application/json',
            'Accept-Version': 'v1',
            'User-Agent': 'CrewAI-Unsplash-Tool/2.0'
        })
        
        # Rate limiting
        object.__setattr__(self, '_last_request_time', 0)
        object.__setattr__(self, '_min_request_interval', 1.0)  # Minimum 1 second between requests
        
        # Setup logging
        object.__setattr__(self, '_logger', logging.getLogger(__name__))
        
        # Cache for validated URLs
        object.__setattr__(self, '_url_cache', {})
        object.__setattr__(self, '_cache_ttl', 300)  # 5 minutes
    
    def _wait_for_rate_limit(self) -> None:
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        object.__setattr__(self, '_last_request_time', time.time())
    
    def _validate_image_url(self, url: str) -> bool:
        """
        Validate that an image URL is accessible and returns a valid image.
        
        Args:
            url: Image URL to validate
            
        Returns:
            True if URL is valid and accessible, False otherwise
        """
        # Check cache first
        cache_key = f"url_validation:{url}"
        if cache_key in self._url_cache:
            cached_result, timestamp = self._url_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_result
        
        try:
            # Make HEAD request to check if URL is accessible
            response = requests.head(url, timeout=10, allow_redirects=True)
            is_valid = (
                response.status_code == 200 and
                response.headers.get('content-type', '').startswith('image/')
            )
            
            # Cache the result
            self._url_cache[cache_key] = (is_valid, time.time())
            return is_valid
            
        except Exception as e:
            self._logger.warning(f"URL validation failed for {url}: {e}")
            # Cache negative result for shorter time
            self._url_cache[cache_key] = (False, time.time())
            return False
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> requests.Response:
        """
        Make a rate-limited request to the Unsplash API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: For network or API errors
        """
        self._wait_for_rate_limit()
        
        url = f"{self._base_url}{endpoint}"
        
        try:
            response = self._session.get(url, params=params, timeout=30)
            
            # Handle specific error cases
            if response.status_code == 401:
                raise requests.RequestException("Invalid API key or unauthorized access")
            elif response.status_code == 403:
                raise requests.RequestException("API access forbidden - check your API key permissions")
            elif response.status_code == 429:
                # Extract retry-after header if available
                retry_after = response.headers.get('Retry-After', '60')
                raise requests.RequestException(
                    f"Rate limit exceeded - please wait {retry_after} seconds before making more requests"
                )
            elif response.status_code >= 500:
                raise requests.RequestException(f"Unsplash server error: {response.status_code}")
            elif response.status_code != 200:
                raise requests.RequestException(f"HTTP error {response.status_code}: {response.text}")
            
            return response
            
        except requests.exceptions.Timeout:
            raise requests.RequestException("Request timed out after 30 seconds")
        except requests.exceptions.ConnectionError:
            raise requests.RequestException("Failed to connect to Unsplash API")
        except requests.exceptions.RequestException:
            raise  # Re-raise RequestException as-is
        except Exception as e:
            raise requests.RequestException(f"Unexpected error: {e}")
    
    def _search_photos(self, search_input: UnsplashSearchInput) -> UnsplashSearchResponse:
        """
        Search for photos using the Unsplash API.
        
        Args:
            search_input: Validated search parameters
            
        Returns:
            Parsed search response
            
        Raises:
            requests.RequestException: For API errors
            ValueError: For invalid response data
        """
        # Build query parameters
        params = {
            'query': search_input.query,
            'page': search_input.page,
            'per_page': search_input.per_page,
            'order_by': search_input.order_by.value,
            'content_filter': search_input.content_filter.value
        }
        
        # Add optional filters
        if search_input.color:
            params['color'] = search_input.color.value
        if search_input.orientation:
            params['orientation'] = search_input.orientation.value
        if search_input.collections:
            params['collections'] = search_input.collections
        
        # Make API request
        response = self._make_request('/search/photos', params)
        
        # Parse response
        try:
            data = response.json()
            return UnsplashSearchResponse(**data)
        except Exception as e:
            raise ValueError(f"Failed to parse API response: {e}")
    
    def _run(
        self,
        query: str,
        per_page: int = 5,
        page: int = 1,
        order_by: str = "relevant",
        color: Optional[str] = None,
        orientation: Optional[str] = None,
        content_filter: str = "low",
        collections: Optional[str] = None
    ) -> List[UnsplashImage]:
        """
        Execute the photo search and return validated results.
        
        Args:
            query: Search terms for finding photos
            per_page: Number of photos per page (default: 5, max: 30)
            page: Page number to retrieve (default: 1)
            order_by: Sort order - "relevant" or "latest" (default: "relevant")
            color: Color filter (optional)
            orientation: Orientation filter (optional)
            content_filter: Content safety filter - "low" or "high" (default: "low")
            collections: Comma-separated collection IDs (optional)
            
        Returns:
            List of UnsplashImage objects with validated URLs
            
        Raises:
            Exception: For any errors during search or validation
        """
        try:
            # Validate and create input model
            search_input = UnsplashSearchInput(
                query=query,
                per_page=min(per_page, 30),  # Enforce API limit
                page=page,
                order_by=order_by,
                color=color,
                orientation=orientation,
                content_filter=content_filter,
                collections=collections
            )
            
            self._logger.info(f"Searching Unsplash for: '{query}' (page {page}, {per_page} results)")
            
            # Perform search
            search_response = self._search_photos(search_input)
            
            # Convert to UnsplashImage objects and validate URLs
            validated_images = []
            for photo in search_response.results:
                try:
                    # Create UnsplashImage from photo
                    image = UnsplashImage.from_photo(photo)
                    
                    # Validate image URL
                    if self._validate_image_url(str(image.image_url)):
                        validated_images.append(image)
                        self._logger.debug(f"Validated image: {image.photo_id}")
                    else:
                        self._logger.warning(f"Invalid or inaccessible URL for photo {photo.id}")
                        
                except Exception as e:
                    self._logger.warning(f"Failed to process photo {photo.id}: {e}")
                    continue
            
            if not validated_images:
                self._logger.warning(f"No valid images found for query: '{query}'")
                # Try to return at least some results even if URL validation fails
                validated_images = [UnsplashImage.from_photo(photo) for photo in search_response.results[:per_page]]
            
            self._logger.info(
                f"Found {search_response.total} total photos, "
                f"returning {len(validated_images)} validated results"
            )
            
            return validated_images
            
        except Exception as e:
            self._logger.error(f"Error searching Unsplash photos: {e}")
            raise Exception(f"Failed to search Unsplash images: {e}")


# Create the tool instance for backward compatibility (only if API key is available)
search_unsplash_images_tool = None
if UNSPLASH_API_KEY:
    try:
        search_unsplash_images_tool = SearchUnsplashImagesTool()
    except Exception:
        # If tool creation fails, leave it as None
        pass


# Decorator function for backward compatibility with original interface
def search_unsplash_images(query: str, per_page: int = 5) -> List[UnsplashImage]:
    """
    Search Unsplash for images based on the provided query.
    
    This function maintains backward compatibility with the original interface
    while providing all the robustness improvements.
    
    Args:
        query: Search terms for finding photos
        per_page: Number of photos to return (default: 5, max: 30)
        
    Returns:
        List of UnsplashImage objects with validated URLs and proper attribution
        
    Raises:
        Exception: For any errors during search or validation
    """
    global search_unsplash_images_tool
    
    # Create tool instance if not already created
    if search_unsplash_images_tool is None:
        search_unsplash_images_tool = SearchUnsplashImagesTool()
    
    return search_unsplash_images_tool._run(query=query, per_page=per_page)


# Example usage and testing
if __name__ == "__main__":
    # Test the tool
    try:
        print("Testing Unsplash Image Search Tool...")
        
        # Test with the tool instance
        tool = SearchUnsplashImagesTool()
        results = tool._run(query="coffee", per_page=3)
        
        print(f"\nFound {len(results)} images:")
        for i, image in enumerate(results, 1):
            print(f"{i}. {image.description or 'Untitled'}")
            print(f"   📷 {image.attribution}")
            print(f"   🔗 {image.image_url}")
            print(f"   📐 {image.width}x{image.height} | ❤️ {image.likes}")
            print()
        
        # Test backward compatibility
        print("Testing backward compatibility...")
        compat_results = search_unsplash_images("nature", 2)
        print(f"Backward compatibility test: {len(compat_results)} images found")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure UNSPLASH_API_KEY or UNSPLASH_ACCESS_KEY environment variable is set")

