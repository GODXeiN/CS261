
# Stores success


# Keys for Success Value dictionary
KEY_FINANCE = 'Finance'
KEY_TEAM = 'Team'
KEY_TIMESCALE = 'Timescale'
KEY_MANAGEMENT = 'Management'
KEY_CODE = 'Code'
KEY_OVERALL = 'Overall'


class RiskAssessment:
    def __init__(self):
        self.set_success_values(0,0,0,0,0,0)

    # Creates a Risk Assessment with the given success parameters (each is a float in the range [0,1])
    def set_success_values(self, finance, timescale, team, code, management, overallSuccess):
        self.successValues = {
            KEY_FINANCE: finance,
            KEY_TIMESCALE: timescale,
            KEY_CODE: code,
            KEY_MANAGEMENT: management,
            KEY_TEAM: team,
            KEY_OVERALL: overallSuccess
        }

    # Attempts to retrieve the success value corresponding to the given key
    # If the key is not in the dictionary, return None
    def get_success_attribute(self, key):
        if key in self.successValues.keys():
            return self.successValues[key]
        return None

    def __str__(self):
        return str(self.successValues)
