from joblib import load
from .projectDf import independent_headers
from pandas import read_csv
from .RiskAssessment import RiskAssessment
from . import logregTrainer as trainer

class RiskAssessmentGenerator:

    def __init__(self):
        # Load all prediction models
        self.financeModel = self.load_model_and_accuracy(trainer.FINANCE_MODEL_SAVE_DEST)
        self.timescaleModel = self.load_model_and_accuracy(trainer.TIMESCALE_MODEL_SAVE_DEST)
        self.codeModel = self.load_model_and_accuracy(trainer.CODE_MODEL_SAVE_DEST)
        self.teamModel = self.load_model_and_accuracy(trainer.TEAM_MODEL_SAVE_DEST)
        self.managementModel = self.load_model_and_accuracy(trainer.MANAGEMENT_MODEL_SAVE_DEST)

        self.overallSuccessModel = self.load_model_and_accuracy(trainer.OVERALL_MODEL_SAVE_DEST)
        print("Loaded all models")


    def load_model_and_accuracy(self, destAndAccuracy):
        (model_dest, accuracy_dest) = destAndAccuracy
        model = load(model_dest)
        # Retrieve the True-Success and False-Failure rates for the model from the save file
        accuracyDf = read_csv(accuracy_dest)
        tsr = accuracyDf.iloc[0]['TSR']
        ffr = accuracyDf.iloc[0]['FFR']
        return (model, tsr, ffr)


    def get_model_confidence(self, state, modelAndAccuracy):
        (model, trueSuccess, falseFailure) = modelAndAccuracy
        # Get the confidence of the model in failure (0) or success (1)
        confProbs = model.predict_proba(state)[0]

        # if confProbs[0] > confProbs[1]:
        #     print("Prediction: Failure")
        # else:
        #     print("Prediction: Success")

        # Determine the overall chance of success by using Conditional Probability & Bayes Formula
        # This is important because the model has a non-zero chance to mis-classify a project as a failure,
        # so this case also contributes to the overall likelihood of success.
        #   SUCCESS = MODEL_SUCCESS * MODEL_ACCURATE + (1-MODEL_FAILURE) * MODEL_INACCURATE
        overallSuccessFloat = confProbs[1] * trueSuccess + confProbs[0] * falseFailure

        # Convert estimation to a probability
        # overallSuccessProb = round(100 * overallSuccessFloat, 2)
        # print("Success:", str(overallSuccessProb) + "%")
        
        return overallSuccessFloat
    

    # Receives a single project state in the form of a pandas data Series
    def generate_ra(self, projSample):
        ra = RiskAssessment()

        # Convert the data point from a row to a vector for input into the models
        projX = projSample[independent_headers].to_numpy().reshape(1,-1)

        # Get the confidence of the model in each attribute being successful
        financeScore = self.get_model_confidence(projX, self.financeModel)
        timescaleScore = self.get_model_confidence(projX, self.timescaleModel)
        codeScore = self.get_model_confidence(projX, self.codeModel)
        managementScore = self.get_model_confidence(projX, self.managementModel)
        teamScore = self.get_model_confidence(projX, self.teamModel)
        overallSuccess = self.get_model_confidence(projX, self.overallSuccessModel)

        ra.set_success_values(financeScore, timescaleScore, teamScore, codeScore, managementScore, overallSuccess)
        return ra
        
