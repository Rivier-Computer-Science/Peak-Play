# URL Local:  http://localhost:8000/run_full_assessment 
# URL Remote: https://peakplay.onrender.com/run_full_assessment




"""
curl -X POST "http://localhost:8000/run_full_assessment" \
     -H "Content-Type: application/json" \
     -d '{
        "form_data": {
            "name": "John Doe",
            "nickname": "JD",
            "gender": "Male",
            "age": "25",
            "height": "5 feet 9 inches",
            "weight": "170 lbs",
            "primary sport": "Basketball",
            "secondary sport": "Soccer",
            "handedness": "Right",
            "position 1": "Point Guard",
            "position 2": "Shooting Guard",
            "position 3": "Small Forward",
            "position 4": "Power Forward",
            "stroke": "Freestyle",
            "position 5": "Center",
            "level of play": "College",
            "performance goals": "Increase vertical jump",
            "sprains": "Ankle",
            "strains": "Hamstring",
            "fractures": "None",
            "dislocations": "Shoulder",
            "overuse & chronic injuries": "Knee pain",
            "head & neck injuries": "None",
            "spinal injuries": "None"
        }
        }'
"""

"""
curl -X POST "http://localhost:8000/run_full_assessment" \
     -H "Content-Type: application/json" \
     -d '{
        "form_data": {
            "name": "John Doe",
            "nickname": "JD",
            "gender": "Male",
            "age": "25",
            "height": "5 feet'9 inches",
            "weight": "170 lbs",
            "primary sport": "Basketball",
            "secondary sport": "Soccer",
            "handedness": "Right",
            "position 1": "Point Guard",
            "position 2": "Shooting Guard",
            "position 3": "Small Forward",
            "position 4": "Power Forward",
            "stroke": "Freestyle",
            "position 5": "Center",
            "level of play": "College",
            "performance goals": "Increase vertical jump",
            "sprains": "Ankle",
            "strains": "Hamstring",
            "fractures": "None",
            "dislocations": "Shoulder",
            "overuse & chronic injuries": "Knee pain",
            "head & neck injuries": "None",
            "spinal injuries": "None"
        }
     }'
"""