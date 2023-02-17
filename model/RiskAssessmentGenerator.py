from RiskAssessment import RiskAssessment
from joblib import load
import logregTrainer as lrt

class RiskAssessmentGenerator:

    def __init__(self):
        # Load all prediction models
        self.financeModel = self.load_model_and_accuracy(lrt.FINANCE_MODEL_SAVE_DEST)
        self.timescaleModel = self.load_model_and_accuracy(lrt.TIMESCALE_MODEL_SAVE_DEST)
        self.codeModel = self.load_model_and_accuracy(lrt.CODE_MODEL_SAVE_DEST)
        self.teamModel = self.load_model_and_accuracy(lrt.TEAM_MODEL_SAVE_DEST)
        self.managementModel = self.load_model_and_accuracy(lrt.MANAGEMENT_MODEL_SAVE_DEST)

        self.overallSuccessModel = self.load_model_and_accuracy(lrt.OVERALL_MODEL_SAVE_DEST)
        print("Loaded all models")

    def load_model_and_accuracy(self, destAndAccuracy):
        (model_dest, accuracy_dest) = destAndAccuracy
        model = load(model_dest)
        accuracyFile = open(accuracy_dest, "r")
        accuracy = float(accuracyFile.read())
        accuracyFile.close()
        return (model, accuracy)


    def get_success_probs(self, state, modelAndAccuracy):
        (model, mdlAccuracy) = modelAndAccuracy
        # Get the confidence of the model in failure (0) or success (1)
        confProbs = model.predict_proba(state)[0]

        # Determine the overall chance of success by using Conditional Probability & Bayes Formula
        # SUCCESS = MODEL_SUCCESS * MODEL_ACCURATE + (1-MODEL_FAILURE) * MODEL_INACCURATE
        overallSuccessEst = confProbs[1] * mdlAccuracy + confProbs[0] * (1-mdlAccuracy)
        # Convert estimation to a probability
        overallSuccessProb = round(100 * overallSuccessEst, 2)

        print("Success:", str(overallSuccessProb) + "%")
        return overallSuccessProb



    # Receives a single project state in the form of a pandas data Series
    def generate_ra(self,projectState):
        ra = RiskAssessment()

        # Get the confidence of the model in each attribute being successful
        financeScore = self.get_success_probs(projectState, self.financeModel)
        teamScore = self.get_success_probs(projectState, self.teamModel)
        managementScore = self.get_success_probs(projectState, self.managementModel)
        codeScore = self.get_success_probs(projectState, self.codeModel)
        timescaleScore = self.get_success_probs(projectState, self.timescaleModel)
        overallSuccess = self.get_success_probs(projectState, self.overallSuccessModel)

        ra.set_success_values(financeScore, timescaleScore, teamScore, codeScore, managementScore, overallSuccess)
        return ra




        



        
