# uvicorn app:app
#
# URL Local:  http://localhost:8000/generate_blog_post
# URL Remote: https://peakplay.onrender.com/generate_blog_post
# Get results: https://peakplay.onrender.com/get_result/taskid

"""
curl -X POST "http://localhost:8000/generate_blog_post" \
     -H "Content-Type: text/plain" \
     -d " "
"""

"""
curl -X GET "http://localhost:8000/get_result/2d5965eb-4ada-4ece-988a-be0458f72687" 
"""

"""
curl -X POST "https://peakplay.onrender.com/generate_blog_post" \
     -H "Content-Type: text/plain" \
     -d " "
"""

"""
curl -X GET "https://peakplay.onrender.com/get_result/14970736-a841-4193-82fc-2bcc528a4b3f" 
"""