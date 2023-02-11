Prototype Files: 
    
    * projectOld.py 
        - defines Project class; contains primitive hard metrics.
        - call .make(...) to initialise the project with random budget/deadline in a given range
        - team experience and size generated arbitrarily
        - budget_tolerance field is a multiplier which can be applied to the budget to find the
            hard budget (i.e. the maximum that can be spent in the worst case); 
            if this is exceeded, the project is definitely a failure.
        - deadline/days_taken represented in days
        - call .gen_result() to randomly generate project cost + days_taken.
            (NOTE: you should run this before .calc_success())
        - call .calc_success() to evaluate the project's success, based on its result (0=Failure; 1=Success)
        - also has fields for Budget Success, Deadline Success and Team Success; 
            these are derived from the metrics and are ignored in the ML models

    * genData.py - generates N=5000 projects and writes each as a CSV line to testData.csv

    * logReg.py
        - loads contents of testData.csv;
        - extracts independent features (those we predict from)
        - extracts dependent variable (binary success/failure)
        - split data into training and test data
        - trains LogisticRegression model on training data
        - tests model accuracy on test data
        - displays classification report (showing accuracy)
        - manually test with a Hard-coded project


Version 2:
    
    * project.py
        - (incomplete) successor of projectOld.py;
        - defines ProjectState class, describing project metrics at a given point
            - note: this will likely be refactored to use numpy 
        - stores a list of project states (each is effectively a snap-shot of metrics at a given timepoint)
        - goals: 
            1) make a Project; 
            2) simulate its development (including events which update metrics)
            3) when project complete, evaluate its success/failure
            4) return a list of states, all labelled with the success/failure metric
            
    * projectDf.py
        - alternate version of project.py which uses a Pandas Dataframe to hold the project states (rather than using custom classes)
        - simpler implementation and dev. will primarily continue on this version

    * genDataStaged.py
        - (incomplete) successor of genData.py
        - will generate N=5000 projects
            - for each one, run its simulation, then write out its labelled states to testData.csv (one per line)
        - currently only generates two projects and prints out their initial state


TODO:

    * Choose events to simulate (e.g. addTeamMember(), delayDevelopment()... etc.)
        - may need additional research for impact of contributing factors
    * Design evaluation function ".evaluate(state)" which:  [STARTED]
        - receives the final project state
        - applies some function (maybe using the values Rai is working on)
        - then returns a score, which can be mapped to Success(1) or Failure(0)
    * Make method to return the success/failure and all states (so GenDataStaged.py can print)
    * Print the states, one per row (easy) 
        

