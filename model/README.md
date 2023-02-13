Data-Generation:

    * projectDf.py
        - defines SimProject class, representing data about a a single artificial project
        - contains a Pandas Dataframe of project states, tracking the project's development over time
        - project status tracked: Planning/Development/Completion/Cancelled
        - last state used to evaluate success of project (score)
        - currently evaluates success by weighted sum of components (primitive implementation)
        - TODO: implement separate model components for score evaluation

    * genDataStaged.py
        - generates fixed number of simulated projects
        - samples given number of states from each project and writes them to testDataStaged.py

    * regLabeller.py (unfinished) 
        - Regression model which predicts overall success based on the metrics from Rai's dataset of contributing factors
        - uses K-Nearest neighbour imputing to "fill" missing gaps
        - model receives hard metrics, team metrics and management metrics; returns arbitrary score
        - will likely be split into separate component models (e.g. one for teams; one for management... etc.) later


Risk-Assessment Model:

    * logregStaged.py
        - loads contents of "testDataStaged.csv";
        - extracts independent features (those we predict from) and dependent variable (binary success/failure)
        - splits data into training and test data
        - trains LogisticRegression model on 50% of data; tests model accuracy on remaining test data
        - displays classification report (showing overall accuracy)
        - dumps model out to "logregmodel.joblib" so it can be loaded and used elsewhere
    
    * manualTest.py 
        - loads LogisticRegression model
        - generates a single project and input a single state from it into the model
        - displays result and the sample for comparison

        
        

