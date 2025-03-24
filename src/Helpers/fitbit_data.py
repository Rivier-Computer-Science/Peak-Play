
class FitBitData:
    def __init__(self, fitbit_data, **kwargs):
        self.fitbit_data = fitbit_data

    def get_fitbit_data(self) -> dict:
        return self.fitbit_data