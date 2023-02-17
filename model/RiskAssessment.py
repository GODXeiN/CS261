KEY_FINANCE = 'Finance'
KEY_TEAM = 'Team'
KEY_TIMESCALE = 'Timescale'
KEY_MANAGEMENT = 'Management'
KEY_CODE = 'Code'

KEY_OVERALL = 'Overall'
KEY_OVERALL_NORM = 'Overall Normalised'

coefficients = {
    KEY_FINANCE: 5.0,
    KEY_TIMESCALE: 5.0,
    KEY_CODE: 1.0,
    KEY_MANAGEMENT: 2.0,
    KEY_TEAM: 2.0
}

class RiskAssessment:

    maxScore = 0.0

    # Creates a Risk Assessment with the given success parameters (each is a float in the range [0,1])
    def __init__(self, finance, timescale, team, code, management):
        self.successValues = {
            KEY_FINANCE: finance,
            KEY_TIMESCALE: timescale,
            KEY_CODE: code,
            KEY_MANAGEMENT: management,
            KEY_TEAM: team
        }

        # Calculate the total score with a weighted sum of components
        overallSuccess = 0
        for (key,val) in self.successValues.items():
            overallSuccess += coefficients[key] * val
        # Store total success in the dictionary
        self.successValues[KEY_OVERALL] = overallSuccess

        # Calculate the maximum possible score if all components have a success value of 1
        if self.maxScore == 0.0:
            for (key, val) in coefficients.items():
                self.maxScore += val

        # Check to avoid dividing by zero
        if self.maxScore > 0.0:
            # Transform the overall assessment success score to range [0,1] by calculating it as 
            # a proportion of the maximum possible score
            self.successValues[KEY_OVERALL_NORM] = overallSuccess / self.maxScore

        # print(self.successValues.items())


    # Attempts to retrieve the success value corresponding to the given key
    # If the key is not in the dictionary, return None
    def get_success_attribute(self, key):
        if key in self.successValues.keys():
            return self.successValues[key]
        return None


    def get_normalised_score(self):
        return self.get_success_attribute(KEY_OVERALL_NORM)


    def __str__(self):
        return str(self.successValues)