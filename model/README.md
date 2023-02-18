Data-Generation:

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


Risk-Assessment Model:

    * logregTrainer.py
        - loads contents of "/data/trainDataStaged.csv";
        - extracts independent features (those we predict from) and the dependent variable (binary success/failure) for each project component (Budget/Timescale/Team/Code/Management, and Overall)
        - splits data into training and test data
        - trains a LogisticRegression model to predict dependent variable using the generated project data
        - each model trained on 50% of data; tests model accuracy on remaining test data
        - displays classification report (showing overall accuracy)
        - dumps models out to "/trained/" so they can be loaded and used elsewhere
    
    * testSingle.py 
        - loads LogisticRegression model
        - generates a single project and inputs a single state from it into the model
        - displays the predicted result compared to the actual simulation of the project success

        
        

