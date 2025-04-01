import json

class AthleteProfile:
    def __init__(self, player_profile, **kwargs):
        self.player_profile = self.convert_athlete_profile(player_profile)

    
    def get_athlete_profile(self) -> dict:
        return self.player_profile    
    
    @staticmethod
    def convert_athlete_profile(player_profile) -> dict:
        '''
            Take a player profile in json string or dict form and return dict
        '''
        if player_profile is not None:
            if isinstance(player_profile, str):
                player_profile = json.loads(player_profile)
            elif isinstance(player_profile, dict):
                return player_profile
            else:
                raise ValueError("player_profile must be a dict or a valid JSON string.")

        if 'form_data' in player_profile:
            return player_profile['form_data']

        else: # default profile
            return {
                    "athlete_name": "John Doe",
                    "athlete_age": 25,
                    "sex": "male",
                    "primary_sport": "soccer",
                    "primary_sport_level": "recreational player",
                    "secondary_sport": "basketball",
                    "secondary_sport_level": "recreational player",
                    "unique_aspect": "exceptional agility"
            }
        
    
             