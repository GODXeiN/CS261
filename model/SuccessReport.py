KEY_FINANCE = 'Finance'
KEY_TEAM = 'Team'
KEY_TIMESCALE = 'Timescale'
KEY_MANAGEMENT = 'Management'
KEY_CODE = 'Code'
KEY_OVERALL = 'Overall'



# Weightings of each factor when calculating the overall success
success_coefficients = {
    KEY_FINANCE: 5.0,
    KEY_TIMESCALE: 5.0,
    KEY_MANAGEMENT: 1.0,
    KEY_CODE: 2.5,
    KEY_TEAM: 2.0
}

class SuccessReport:

    def __init__(self):
        self.set_success_values(0,0,0,0,0)
        
        
    # Creates a Risk Assessment with the given success parameters (each is a float in the range [0,1])
    def set_success_values(self, finance, timescale, team, code, management):
        self.successValues = {
            KEY_FINANCE: finance,
            KEY_TIMESCALE: timescale,
            KEY_CODE: code,
            KEY_MANAGEMENT: management,
            KEY_TEAM: team
        }

        # Calculate the total score with a weighted sum of components
        overallSuccess = 0.0
        maxPossibleScore = 0.0
        for (key, val) in self.successValues.items():
            overallSuccess += success_coefficients[key] * val
            maxPossibleScore += success_coefficients[key]

        # Check to avoid division by zero
        if maxPossibleScore > 0.0:
            # Transform the overall assessment success score to range [0,1] 
            # by calculating it as a proportion of the maximum possible score
            self.successValues[KEY_OVERALL] = overallSuccess / maxPossibleScore


    # Attempts to retrieve the success value corresponding to the given key
    # If the key is not in the dictionary, return None
    def get_success_attribute(self, key):
        if key in self.successValues.keys():
            return self.successValues[key]
        return None


    # Convert each success value into 1 (if value >= 0.5), or 0 (if value < 0.5)
    # and return the dictionary of the binarized values.
    def get_binary_successes(self):
        binSuccesses = {}

        for (key, success) in self.successValues.items():
            if success > 0.6:
                binSuccesses[key] = 1
            else:
                binSuccesses[key] = 0

        return binSuccesses


    def get_success_values(self):
        return self.successValues


    def get_normalised_score(self):
        return self.get_success_attribute(KEY_OVERALL)


    def __str__(self):
        s = "\n  -----  SUCCESS REPORT  -----  "
        for (key, val) in self.successValues.items():
            s += "\n  * " + key.ljust(12) + " = "
            if val >= 0.5:
                s += "Success (1)"
            else:
                s += "Failure (0)"
        return s
