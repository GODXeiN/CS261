# Overview:
Preface for the Risk-Assessment-Model (RAM) and Machine-Learning component.

This section is split into two primary elements: Data-Generation, and Success-Prediction.


# Data-Generation:
This section produces the labelled data-set of projects ("/data/trainDataStaged.csv") which is used to train the Machine-Learning model.
The ML only learns relationships which appear in the data-set, so its important that we have as many rows as possible with high variation to avoid overfitting the model to the specific data we give it (i.e. we want it to generalise well).

The Data-Generation is effectively the mass simulation of projects with arbitrary starting parameters. 
For each simulated project, the progress is maintained; progress increases as a function of the team and various soft metrics (it may also decrease probabilitically). When the project progress reached 100%, the project is marked as complete and the simulation stops. Now, the module evaluates the final project state based on the five independent key Aspects (Finance, Deadline, Team, Code, Management), producing binary values for success for each component (i.e. 0 = Failure, 1 = Success). The overall project evaluation is calculated with a weighted score of these individual aspects. For each project, this results in 6 bits (0 or 1) indicating if the project succeeded in that area. Then one ML model is trained to recognise the attribute values which lead to success/failure for each component and another model considers the overall success. The component-wise evaluation allows greater granularity in the feedback provided to the user.

    * projectDf.py
        - defines SimProject class, representing data about a a single artificial project
        - contains a Pandas Dataframe of project states, tracking the project's development over time
        - project status tracked: Planning/Development/Completion/Cancelled
        - last state used to evaluate success of project (score)
        - project success evaluated based on the last state; .evaluate() returns a SuccessReport

    * genDataStaged.py
        - generates fixed number of simulated projects
        - samples given number of states from each project and writes them to trainDataStaged.py/testDataStaged.py, depending on the mode selected

    * RiskAssessment.py
        - defines a class describing success prediction for a given project state
        - include fields for success of Budget/Timescale/Code/Team/Management and Overall project success
        - each field is a float in the range [0,1], representing the expected likelihood of that attribute succeeding
        - is instantiated based on model predictions obtained by RiskAssessmentGenerator

    * RiskAssessmentGenerator.py
        - loads trained models for prediction of each project attribute
        - generate_ra(...) takes a project state and runs the model on that state to obtain confidence levels for each prediction
        - then, the confidence levels are probabilistically combined with the recorded accuracy of the model, to determine an estimate for the actual likelihood of the given result (success/failure) occurring
        - populates a RiskAssessment object based on the calculated confidence levels

    * SuccessReport.py
        - defines a class for representing/calculating overall success of a simulated project
        - only used in the data-generation (i.e. genDataStaged.py)


# Success-Prediction Model:
The model consists of 6 Logistic Regression modules each of which predict one success field of the project.
All the models are trained on the full training dataset and all fields, so the model should also learns implicit relationships, rather than being specialised for the individual metrics which are relevant to the aspect in question.
For example, the Finance model is not trained specifically on the fields which impact finance (Budget, Cost, Team Expertise).
These models are exported to the /trained/ directory using Joblib.dump and can be loaded back in with Joblib.load.

Then, the Risk-Assessment class describes a single prediction provided by the RiskAssessmentGenerator class (RAG). Given a project snapshot (i.e. a set of all project metrics for some point in time), the RAG.generate_ra() method runs all predictive models on the snapshot and gets the confidence score for their predictions. Then, by applying Bayes Formula for Conditional Probability with the accuracy of each model (recorded after testing), we can determine the overall probability that the project succeeds, irrespective of the model. As such, we are more likely to receive an accurate prediction since we consider the chance that the model is incorrect.

    * logregTrainer.py
        - loads contents of "/data/trainDataStaged.csv";
        - extracts independent features (those we predict from) and the dependent variable (binary success/failure) for each project component (Budget/Timescale/Team/Code/Management, and Overall)
        - splits data into training and test data
        - trains a LogisticRegression model to predict dependent variable using the generated project data
        - each model trained on 50% of data; tests model accuracy on remaining test data
        - displays classification report (showing overall accuracy)
        - dumps models out to "/trained/" so they can be loaded and used elsewhere

    * testBulk.py
        - loads contents of "/data/testDataStaged.csv"
        - loads all 6 trained models
        - runs Success-Prediction models against test data
        - displays Classification Report (accuracy) of each model

    * testSingle.py 
        - loads LogisticRegression model
        - generates a single project and inputs a single state from it into the model
        - displays the predicted result compared to the actual simulation of the project success

        