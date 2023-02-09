# import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# create the database interface
db = SQLAlchemy()

class Manager(db.Model):
    __tablename__='Manager'
    managerID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    emailAddr = db.Column(db.String(50))
    firstName = db.Column(db.String(50))
    hashedPW = db.Column(db.String(150))

    def __init__(self, emailAddr, firstName, hashedPW):
        self.emailAddr = emailAddr
        self.firstName = firstName
        self.hashedPW = hashedPW

class Project(db.Model):
    __tablename__='Project'
    projectID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    managerID = db.Column(db.Integer, db.ForeignKey('Manager.managerID'))
    dateCreated = db.Column(db.Integer)
    title = db.Column(db.String(50))
    dateLastSurveyed = db.Column(db.Integer)
    dateLastRiskCalculation = db.Column(db.Integer)
    updateInterval = db.Column(db.Integer)

    def __init__(self, managerID, dateCreated, title, dateLastSurveyed, dateLastRiskCalculation, updateInterval):
        self.managerID = managerID
        self.dateCreated = dateCreated
        self.title = title
        self.dateLastSurveyed = dateLastSurveyed
        self.dateLastRiskCalculation =  dateLastRiskCalculation
        self.updateInterval = updateInterval

class Deadline(db.Model):
    __tablename__='Deadline'
    deadlineID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    projectID = db.Column(db.Integer, db.ForeignKey('Project.projectID'))
    title = db.Column(db.String(50))
    deadlineDate = db.Column(db.Integer)
    achieved = db.Column(db.Integer)

    def __init__(self, projectID, title, deadlineDate, achieved):
        self.projectID = projectID
        self.title = title
        self.deadlineDate = deadlineDate
        self.achieved = achieved

class Hard_Metrics(db.Model):
    __tablename__='Hard_Metrics'
    projectID = db.Column(db.Integer, db.ForeignKey('Project.projectID'), primary_key = True)
    date = db.Column(db.Integer, primary_key = True)
    budget = db.Column(db.Integer)
    costToDate = db.Column(db.Integer)
    deadline = db.Column(db.Integer)
    status = db.Column(db.Integer)

    def __init__(self, projectID, date, budget, costToDate, deadline, status):
        self.projectID = projectID
        self.date = date
        self.budget = budget
        self.costToDate = costToDate
        self.deadline = deadline
        self.status = status

class Risk(db.Model):
    __tablename__='Risk'
    projectID = db.Column(db.Integer, db.ForeignKey('Project.projectID'), primary_key = True)
    date = db.Column(db.Integer, primary_key = True)
    riskLevel = db.Column(db.Float)

    def __init__(self, projectID, date, riskLevel):
        self.projectID = projectID
        self.date = date
        self.riskLevel = riskLevel

class Git_Link(db.Model):
    __tablename__='Git_Link'
    projectID = db.Column(db.Integer, db.ForeignKey('Project.projectID'), primary_key = True)
    gitToken = db.Column(db.String(100))
    repositoryURL = db.Column(db.String(100))

    def __init__(self, projectID, gitToken, repositoryURL):
        self.projectID = projectID
        self.gitToken = gitToken
        self.repositoryURL = repositoryURL

class Worker(db.Model):
    __tablename__='Worker'
    workerID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    emailAddr = db.Column(db.String(50))
    experienceRank = db.Column(db.Integer)

    def __init__(self, emailAddr, experienceRank):
        self.emailAddr = emailAddr
        self.experienceRank = experienceRank

class Works_On(db.Model):
    __tablename__='Works_On'
    projectID = db.Column(db.Integer, db.ForeignKey('Project.projectID'), primary_key = True)
    workerID = db.Column(db.Integer, db.ForeignKey('Worker.workerID'), primary_key = True)

    def __init__(self, projectID, workerID):
        self.projectID = projectID
        self.workerID = workerID

class Survey_Response(db.Model):
    __tablename__='Survey_Response'
    projectID = db.Column(db.Integer, db.ForeignKey('Project.projectID'), primary_key = True)
    workerID = db.Column(db.Integer, db.ForeignKey('Worker.workerID'), primary_key = True)
    date = db.Column(db.Integer, primary_key = True)
    metricOne = db.Column(db.Float)
    metricTwo = db.Column(db.Float)
    metricThree = db.Column(db.Float)
    metricFour = db.Column(db.Float)
    metricFive = db.Column(db.Float)

    def __init__(self, projectID, workerID, date, metricOne, metricTwo, metricThree, metricFour, metricFive):
        self.projectID = projectID
        self.workerID = workerID
        self.date = date
        self.metricOne = metricOne
        self.metricTwo = metricTwo
        self.metricThree = metricThree
        self.metricFour = metricFour
        self.metricFive = metricFive