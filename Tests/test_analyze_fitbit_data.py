# Test cases

# TODO: Turn these into real unit tests
# URL Local:  http://localhost:8000/analyze_fitbit_data
# URL Remote: https://peakplay.onrender.com/analyze_fitbit_data

"""
curl -X POST "http://localhost:8000/analyze_fitbit_data" \
     -H "Content-Type: text/plain" \
     -d "Player Profile: 16-Year-Old Left-Handed Starting Pitcher (Honors Student)
Name: John Ball
Age: 16
Height: 6'1\"
Weight: 180 lbs
Dominant Hand: Left
Position: Starting Pitcher
Throws/Bats: Left/Right
Academic Standing: Honors Student (4.0 GPA, AP Classes in Physics and Biology)
Career Aspiration: College Baseball with MLB Potential

Pitching Metrics:
Fastball Velocity: 85-88 mph
Breaking Ball (Curveball/Slider): 72-75 mph (with good movement)
Changeup: 76-78 mph
Spin Rate:
    Fastball: 2200-2400 RPM
    Curveball: 2500+ RPM
Control: Above average, walks less than 2 batters per 7 innings
Pitching Style: Power pitcher with solid off-speed pitches
Endurance: Can pitch 6-7 innings at a high level

Fitbit Data:
**Biometric Data for John Ball - 7-Day Sample**  

**Day 1:**  
Steps: 12,456  
Active Minutes: 89  
Calories Burned: 3,200  
Resting Heart Rate: 52 bpm  
Max Heart Rate: 181 bpm (bullpen session)  
Sleep: 7h 45m (Deep: 2h 10m, Light: 4h 30m, REM: 1h 5m)  
HRV: 85 ms  
Stress Level: Moderate  

**Day 2:**  
Steps: 9,874  
Active Minutes: 76  
Calories Burned: 2,900  
Resting Heart Rate: 50 bpm  
Max Heart Rate: 172 bpm (weight training)  
Sleep: 8h 10m (Deep: 2h 30m, Light: 4h 50m, REM: 50m)  
HRV: 90 ms  
Stress Level: Low  

**Day 3:**  
Steps: 11,532  
Active Minutes: 82  
Calories Burned: 3,150  
Resting Heart Rate: 51 bpm  
Max Heart Rate: 185 bpm (game day)  
Sleep: 7h 20m (Deep: 1h 50m, Light: 4h 40m, REM: 50m)  
HRV: 80 ms  
Stress Level: High  

**Day 4:**  
Steps: 8,973  
Active Minutes: 65  
Calories Burned: 2,750  
Resting Heart Rate: 48 bpm  
Max Heart Rate: 168 bpm (recovery day, light throwing)  
Sleep: 8h 35m (Deep: 2h 40m, Light: 5h 10m, REM: 45m)  
HRV: 95 ms  
Stress Level: Low  

**Day 5:**  
Steps: 12,220  
Active Minutes: 91  
Calories Burned: 3,250  
Resting Heart Rate: 50 bpm  
Max Heart Rate: 179 bpm (bullpen session, sprint drills)  
Sleep: 7h 55m (Deep: 2h 15m, Light: 4h 50m, REM: 50m)  
HRV: 88 ms  
Stress Level: Moderate  

**Day 6:**  
Steps: 10,542  
Active Minutes: 79  
Calories Burned: 3,000  
Resting Heart Rate: 49 bpm  
Max Heart Rate: 174 bpm (strength training)  
Sleep: 8h 20m (Deep: 2h 20m, Light: 5h 10m, REM: 50m)  
HRV: 92 ms  
Stress Level: Low  

**Day 7:**  
Steps: 13,102  
Active Minutes: 95  
Calories Burned: 3,350  
Resting Heart Rate: 51 bpm  
Max Heart Rate: 183 bpm (game day)  
Sleep: 7h 10m (Deep: 1h 45m, Light: 4h 20m, REM: 1h 5m)  
HRV: 78 ms  
Stress Level: High
"
"""