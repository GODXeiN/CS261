from flask import Blueprint, render_template, request, flash, redirect, url_for, session, Flask
from flask_login import login_user, login_required, current_user
from .models import Project, Git_Link, Hard_Metrics, Worker, Deadline, Works_On, End_Result, Survey_Response, Risk
from . import db, app
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from .suggestionSys import suggSys
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

views = Blueprint('views', __name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'gerokenpack@gmail.com'
app.config['MAIL_PASSWORD'] = 'kwkkhixwxpdwiuby'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
scheduler = BackgroundScheduler(daemon=True)

def scheduledTask():
    with app.app_context():
        today_unix=int(datetime.now().timestamp())
        projects = Project.query.filter(Project.projectID > 0).order_by(Project.projectID.desc())
        for project in projects:
            devs = []
            hmetrics = Hard_Metrics.query.filter_by(projectID = project.projectID).order_by(Hard_Metrics.date.desc()).first()
            secondsInterval = project.updateInterval * 24 * 60 * 60
            lastSurveyed = project.dateLastSurveyed
            pID = project.projectID
            if (int(hmetrics.status) == 0) and ((secondsInterval + lastSurveyed) <= today_unix):
                project.dateLastSurveyed = today_unix
                db.session.commit()
                k=Works_On.query.filter_by(projectID = pID).all()
                for entry in k:
                    q = Worker.query.filter_by(workerID = entry.workerID).first()
                    devs.append((entry.workerID,q.emailAddr)) 
            if devs:
                for developer in devs:
                    msg = Message('Periodic Survey', sender = 'gerokenpack@gmail.com', recipients = [f'{developer[1]}'])
                    msg.html = f"""<p> Hello,</p> <p>You have been prompted to answer a periodic survey for the project {project.title}. Your developer ID is {developer[0]}. You can access the survey using the following link: http://127.0.0.1:5000/survey_auth/{pID}</p> <p>This is an automatic email. Do not reply.</p><img src="https://i.imgur.com/x044DiX.png" width="100" height="100" /> """
                    mail.send(msg)    

scheduler.add_job(func=scheduledTask, trigger="interval", seconds=86400)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

@views.route('/home', methods=['GET','POST'])
@login_required
def home():
    session.pop('pID', None)
    finished = []
    ongoing = []
    projects = Project.query.filter_by(managerID = current_user.managerID).all()
    for entry in projects:
        hmetrics = Hard_Metrics.query.filter_by(projectID = entry.projectID).order_by(Hard_Metrics.date.desc()).first()
        if int(hmetrics.status) == 0:
            ongoing.append((entry.title,hmetrics.budget,datetime.utcfromtimestamp(entry.dateCreated).strftime('%Y-%m-%d'),datetime.utcfromtimestamp(hmetrics.deadline).strftime('%Y-%m-%d'), entry.projectID))
        else:
            finished.append((entry.title,hmetrics.budget,datetime.utcfromtimestamp(entry.dateCreated).strftime('%Y-%m-%d'),datetime.utcfromtimestamp(hmetrics.deadline).strftime('%Y-%m-%d'), entry.projectID))
    if request.method == "POST":
        # record the user name
        session["pID"] = request.form['details']
        # redirect to the main page
        return redirect("/view")
    return render_template("home.html", user=current_user, ongoing=ongoing, finished=finished)

@views.route('/create_project', methods=['GET','POST'])
@login_required
def create_project():
    today=datetime.now()
    today_unix=int(datetime.now().timestamp())
    if request.method=='POST':
        title=request.form.get('title')
        deadline=request.form.get('deadline')
        budget=request.form.get('budget')
        
        date_time_obj = datetime.strptime(deadline, '%Y-%m-%d')
        unix_deadline=int(date_time_obj.timestamp())
        if len(title)>0:
            managerid=current_user.get_id()
            project=Project(managerID=managerid, dateCreated=today_unix, title=title, dateLastSurveyed=today_unix,dateLastRiskCalculation=today_unix,updateInterval=4)
            db.session.add(project)
            db.session.commit()
            proj_id=project.get_id()

            hard_metrics=Hard_Metrics(proj_id, date=today_unix, budget=budget, costToDate=0, deadline=unix_deadline, status=0)
            db.session.add(hard_metrics)
            db.session.commit()
            return redirect("/home")
        
        else:
            flash('Something went wrong with your inputs')

    #Post on refresh page bug!!
    return render_template("create_project.html")

@views.route('/end_project', methods=['GET','POST'])
@login_required
def end_project():
    today_unix=int(datetime.now().timestamp())

    if session.get('pID') is None:
        return redirect("/home")
    
    if Hard_Metrics.query.filter_by(projectID = session.get('pID')).first().status != 0:
        return redirect("/view")
    
    pID = session['pID']
    projectName = Project.query.filter_by(projectID=pID).first().title
    hm = Hard_Metrics.query.filter_by(projectID = pID).order_by(Hard_Metrics.date.desc()).first()

    if request.method=='POST':
        financeMetric=request.form.get('questionTwo')
        timescaleMetric=request.form.get('questionThree')
        managementMetric=request.form.get('questionFour')
        teamMetric=request.form.get('questionFive')
        codeMetric=request.form.get('questionSix')
        new_status=request.form.get('status')

        end = End_Result(projectID = pID, financeMetric=financeMetric, timescaleMetric=timescaleMetric, managementMetric=managementMetric, teamMetric=teamMetric, codeMetric=codeMetric)
        new_metrics = Hard_Metrics(projectID=pID, date=today_unix, budget=hm.budget, costToDate=hm.costToDate, deadline=hm.deadline,status=new_status)
        db.session.add(end)
        db.session.add(new_metrics)
        db.session.commit()

        return redirect("/view")

    return render_template("end_project.html", projectName=projectName)

@views.route('/view', methods=['GET','POST'])
@login_required
def view():

    finished = True

    if session.get('pID') is None:
        return redirect("/home")
    
    today_unix=int(datetime.now().timestamp())

    if session.get('pID') is None:
        return redirect("/home")
    if Hard_Metrics.query.filter_by(projectID = session.get('pID')).order_by(Hard_Metrics.date.desc()).first().status != 0:
        finished = False
    
    pID = session['pID']
    projectName = Project.query.filter_by(projectID=pID).first().title

    if request.method == 'POST':
        devs = []
        if request.form['submit_button'] == 'Send Email':
            projects = Project.query.filter_by(projectID = pID)
            hmetrics = Hard_Metrics.query.filter_by(projectID = pID).order_by(Hard_Metrics.date.desc()).first()
            if (int(hmetrics.status) == 0):
                projects.dateLastSurveyed = today_unix
                db.session.commit()
                k=Works_On.query.filter_by(projectID = pID).all()
                for entry in k:
                    q = Worker.query.filter_by(workerID = entry.workerID).first()
                    devs.append((entry.workerID,q.emailAddr)) 
                if devs:
                    for developer in devs:
                        msg = Message('Periodic Survey', sender = 'gerokenpack@gmail.com', recipients = [f'{developer[1]}'])
                        msg.html = f"""<p> Hello,</p> <p>You have been prompted to answer a periodic survey for the project {projectName}. Your developer ID is {developer[0]}. You can access the survey using the following link: http://127.0.0.1:5000/survey_auth/{pID}</p> <p>This is an automatic email. Do not reply.</p><img src="https://i.imgur.com/x044DiX.png" width="100" height="100" /> """
                        mail.send(msg)

        elif request.form['submit_button'] == 'Calculate Risk':
            pass # do something else
        else:
            pass # unknown

    return render_template("view.html", projectName=projectName, finished=finished)

@views.route('/faq')
@login_required
def faq():
    return render_template("faq.html")

@views.route('/suggestions')
@login_required
def suggestions():
    if session.get('pID') is None:
        return redirect("/home")
    
    if Hard_Metrics.query.filter_by(projectID = session.get('pID')).first().status != 0:
        return redirect("/view")
    
    pID = session['pID']

    risk = Risk.query.filter_by(projectID = pID).order_by(Risk.date.desc()).first()

    riskFinance = 0
    riskCode = 0
    riskManagement = 0
    riskTimescale = 0
    riskTeam = 0

    if risk:
        riskFinance = risk.riskFinance
        riskCode = risk.riskCode
        riskManagement = risk.riskManagement
        riskTimescale = risk.riskTimescale
        riskTeam = risk.riskTeam

    suggestions = suggSys(riskFinance, riskTimescale, riskCode, riskTeam, riskManagement)

    projectName = Project.query.filter_by(projectID=pID).first().title

    
    return render_template("suggestions.html", projectName=projectName, budget=suggestions.getBudgetRisk(), code=suggestions.getCodeRisk(), management=suggestions.getManagementRisk(), timescale = suggestions.getTimeRisk(), team = suggestions.getTeamRisk())

@views.route('/int_deadline', methods=['GET','POST'])
@login_required
def int_deadline():
    pID=session.get('pID')
    if session.get('pID') is None:
        return redirect("/home")
    if Hard_Metrics.query.filter_by(projectID = pID).first().status != 0:
        return redirect("/view")
    project_deadline=Hard_Metrics.query.filter_by(projectID=pID).order_by(Hard_Metrics.date.desc()).first().deadline
    date=0
    if request.method=='POST':
        title=request.form.get('title')
        date=request.form.get('int_dd')
        date_time_obj = datetime.strptime(date, '%Y-%m-%d')
        unix_date=int(date_time_obj.timestamp())

        if project_deadline>unix_date:
            existing_title=Deadline.query.filter_by(title=title).first()
            if not existing_title:
                new_deadline=Deadline(projectID=pID,title=title,deadlineDate=date, achieved=0)
                db.session.add(new_deadline)
                db.session.commit()
                flash('Internal deadline successfully added.', category='success')
            else:
                flash('Please try a different title. Current one is taken', category='warning')
        else:
            flash('Failed to add internal deadline. The date must be less than or equal to the final project deadline.', category='error')
    deadlines=Deadline.query.filter_by(projectID=pID).all()
    
    return render_template("int_deadline.html", deadlines=deadlines, date=date)

@views.route('/complete_deadline/<id>/<int:status>')
def complete_deadline(id,status):
    ded=Deadline.query.filter_by(deadlineID=id).first()

    if ded:
        ded.achieved=status
        db.session.commit()
        if status==1:
            flash('Deadline status has been set to: SUCCESS.', category='success')
        elif status==2:
            flash('Deadline status has been set to: FAILED.', category='warning')

        return redirect(url_for('views.int_deadline'))
    else:
        flash('Something went wrong.', category='error')
    return redirect(url_for('views.int_deadline'))
@views.route('/manage_devs', methods=['GET','POST'])
@login_required
def manage_devs():

    devs=[]

    if session.get('pID') is None:
        return redirect("/home")
    
    if Hard_Metrics.query.filter_by(projectID = session.get('pID')).first().status != 0:
        return redirect("/view")
    
    if request.method=='POST':
        dev_email=request.form.get('dev_email')
        all_works_on=Works_On.query.filter_by(projectID=session['pID']).all()
        i=0
        all_workers=[]
        for item in all_works_on:
            worker=Worker.query.filter_by(workerID=item.workerID).first()
            email=worker.emailAddr
            all_workers.append(email)
            
        if dev_email not in all_workers:
            new_dev=Worker(emailAddr=dev_email, experienceRank=None)
            db.session.add(new_dev)
            new_worksOn=Works_On(projectID = session['pID'], workerID = Worker.query.filter_by(emailAddr=dev_email).order_by(Worker.workerID.desc()).first().workerID)
            db.session.add(new_worksOn)
            db.session.commit()
            flash('Developer added successfully.', category='success')

        else:
            flash('Developer already exists in current project.', category='error')
    k=Works_On.query.filter_by(projectID = session['pID']).all()

    for entry in k:
        q = Worker.query.filter_by(workerID = entry.workerID).first()
        devs.append((entry.workerID,q.emailAddr))
    
 
        
        
    #going from the user page to manage dev page gets an error once you submit
    return render_template("manage_devs.html", devs=devs)

@views.route('/survey_auth/<projectID>', methods=['GET','POST'])
def survey_auth(projectID):
    if request.method=='POST':
        email=request.form.get('email')
        workerID=request.form.get('workerID')
        worker=Worker.query.filter_by(emailAddr=email, workerID=workerID).first()
        if worker:
            workerExperience = worker.experienceRank
            if Works_On.query.filter_by(workerID=workerID, projectID=projectID).first():
                session['wID'] = workerID
                if workerExperience == None:
                    session['psID'] = projectID
                    return redirect('/initial_survey')
                else:
                    return redirect(f'/survey/{projectID}')
            else:
                flash('Could not find the developer associated with this project.', category='error')
        else:
            flash('Could not find the developer associated with this project.', category='error')

    return render_template("mail_auth.html", projectID=projectID)


@views.route('/initial_survey', methods=['GET','POST'])
def initial_survey():
    if session.get('psID') is None or session.get('wID') is None:
        return redirect("/home")
    
    wID = session['wID']
    psID = session['psID']

    worker=Worker.query.filter_by(workerID=wID).first()

    if request.method=='POST':
        experience=request.form.get('questionThree')
        planning=request.form.get('questionTwo')
        worker.experienceRank = experience
        worker.planning = planning
        db.session.commit()
        return redirect(f'/survey/{psID}')

    
    return render_template("initial_survey.html")

@views.route('/survey/<projectID>', methods=['GET','POST'])
def survey(projectID):
    session.pop('psID', None)
    if session.get('wID') is None:
        return redirect("/home")
    
    today_unix=int(datetime.now().timestamp())

    last_submission = Survey_Response.query.filter_by(workerID = session['wID'], projectID=projectID).order_by(Survey_Response.date.desc()).first()
    interval = int(Project.query.filter_by(projectID = projectID).first().updateInterval) * 24 * 60 * 60
    lastSurveyed = int(Project.query.filter_by(projectID = projectID).first().dateLastSurveyed)

    if last_submission:
        if (last_submission.date + interval > lastSurveyed):
            flash('You have already filled in the survey for the given time interval', category='error')
            return redirect(f"/survey_auth/{projectID}")


    if request.method=='POST':
        managementMetric = request.form.get('questionOne')
        commitmentMetric = request.form.get('questionTwo')
        communicationMetric = request.form.get('questionThree')
        happinessMetric = request.form.get('questionFour')
        survey = Survey_Response(projectID=projectID, workerID=session['wID'], date=today_unix, managementMetric=managementMetric, commitmentMetric=commitmentMetric, communicationMetric=communicationMetric, happinessMetric=happinessMetric)
        db.session.add(survey)
        db.session.commit()
        return redirect('/home')
    
    return render_template("periodic_survey.html")
    
     
@views.route('/delete_dev/<id>')
def delete_dev(id):
    dev=Worker.query.filter_by(workerID=id).first()
    work = Works_On.query.filter_by(workerID=id).first()
    if dev:
        db.session.delete(dev)
        db.session.delete(work)
        db.session.commit()
        flash('Developer has been successfully deleted.', category='warning')
        return redirect(url_for('views.manage_devs'))
    else:
        flash('Something went wrong.', category='error')
    return redirect(url_for('views.manage_devs'))

@views.route('/project_details', methods=['GET','POST'])
@login_required
def project_details():
    if session.get('pID') is None:
        return redirect("/home")
    
    url = "Not Found"
    token = "Not Found"

    pID = session['pID']
    
    project_details=Project.query.filter_by(projectID=pID).first()
    hard_metrics=Hard_Metrics.query.filter_by(projectID=pID).order_by(Hard_Metrics.date.desc()).first()
    old_deadline=hard_metrics.deadline
    old_budget=hard_metrics.budget
    old_cost=hard_metrics.costToDate
    git=Git_Link.query.filter_by(projectID=pID).first()
    
    budget=old_budget
    cost=old_cost
    #here we must include the project-specific values. The following is generic as in project id is just 1

    if git:
        url = git.repositoryURL
        token = git.gitToken

    if request.method=='POST':
        new_title=request.form.get('new_title')
        new_budget=request.form.get('new_budget')
        new_deadline=request.form.get('new_deadline')
        update_interval=request.form.get('update_interval')
        cost_to_date=request.form.get('cost_to_date')
        git_token=request.form.get('git_token')
        git_link=request.form.get('git_link')
        int_deadline=request.form.get('int_deadline')
        int_date=request.form.get('deadline')

        proj_id=project_details.get_id()
        today_unix=int(datetime.now().timestamp())        

        if new_title:
            project_details.title=new_title
            db.session.commit()
            
        if new_budget and not new_deadline and not cost_to_date:
            new_hm=Hard_Metrics(projectID=proj_id, date=today_unix, budget=new_budget, costToDate=old_cost, deadline=old_deadline, status=0)
            db.session.add(new_hm)
            db.session.commit()
            budget= new_hm.budget
            cost=hard_metrics.costToDate
            if budget<cost:
                excess=(cost/budget)*100
                flash("Warning! Your project's current cost exceeds the budget by " + str(round(excess,2)) + "%.", category='warning')
        
        if new_budget and new_deadline and not cost_to_date:
            date_time_obj = datetime.strptime(new_deadline, '%Y-%m-%d')
            unix_deadline=int(date_time_obj.timestamp())
            new_hm=Hard_Metrics(projectID=project_details.get_id(), date=today_unix, budget=new_budget, costToDate=old_cost, deadline=unix_deadline, status=0)
            db.session.add(new_hm)
            db.session.commit()
            budget= new_hm.budget
            cost=hard_metrics.costToDate
            if budget<cost:
                excess=(cost/budget)*100
                flash("Warning! Your project's current cost exceeds the budget by " + str(round(excess,2)) + "%.", category='warning')
            if old_deadline>unix_deadline:
                flash('Warning. The updated deadline is earlier than the last one!', category='warning')

        if new_budget and not new_deadline and cost_to_date:
            new_hm=Hard_Metrics(projectID=project_details.get_id(), date=today_unix, budget=new_budget, costToDate=cost_to_date, deadline=old_deadline, status=0)
            db.session.add(new_hm)
            db.session.commit()
            budget= new_hm.budget
            cost=new_hm.costToDate
            if budget<cost:
                excess=(cost/budget)*100
                flash("Warning! Your project's current cost exceeds the budget by " + str(round(excess,2)) + "%.", category='warning')
           
        if new_deadline and not cost_to_date and not new_budget:
            date_time_obj = datetime.strptime(new_deadline, '%Y-%m-%d')
            unix_deadline=int(date_time_obj.timestamp())
            new_hm=Hard_Metrics(projectID=project_details.get_id(), date=today_unix, budget=old_budget, costToDate=old_cost, deadline=unix_deadline, status=0)
            db.session.add(new_hm)
            db.session.commit()            
            if old_deadline>unix_deadline:
                flash('Warning. The updated deadline is earlier than the last one!', category='warning')

        if cost_to_date and not new_deadline and not new_budget:
            new_hm=Hard_Metrics(projectID=project_details.get_id(), date=today_unix, budget=old_budget, costToDate=cost_to_date, deadline=old_deadline, status=0)
            db.session.add(new_hm)
            db.session.commit()
            budget=hard_metrics.budget
            cost=new_hm.costToDate
            if budget<cost:
                excess=(cost/budget)*100
                flash("Warning! Your project's current cost exceeds the budget by " + str(round(excess,2)) + "%.", category='warning')

        if not new_budget and new_deadline and cost_to_date:
            date_time_obj = datetime.strptime(new_deadline, '%Y-%m-%d')
            unix_deadline=int(date_time_obj.timestamp())
            new_hm=Hard_Metrics(projectID=project_details.get_id(), date=today_unix, budget=old_budget, costToDate=cost_to_date, deadline=unix_deadline, status=0)
            db.session.add(new_hm)
            db.session.commit()
            budget=hard_metrics.budget
            cost=new_hm.costToDate
            
            if budget<cost:
                excess=(cost/budget)*100
                flash("Warning! Your project's current cost exceeds the budget by " + str(round(excess,2)) + "%.", category='warning')

        if new_budget and new_deadline and cost_to_date:
            date_time_obj = datetime.strptime(new_deadline, '%Y-%m-%d')
            unix_deadline=int(date_time_obj.timestamp())
            new_hm=Hard_Metrics(projectID=project_details.get_id(), date=today_unix, budget=new_budget, costToDate=cost_to_date, deadline=unix_deadline, status=0)
            db.session.add(new_hm)
            db.session.commit()
            budget=new_hm.budget
            cost=new_hm.costToDate
            
            if budget<cost:
                excess=(cost/budget)*100
                flash("Warning! Your project's current cost exceeds the budget by " + str(round(excess,2)) + "%.", category='warning')
            if old_deadline>unix_deadline:
                flash('Warning. The updated deadline is earlier than the last one!', category='warning')

        if git:
            if git_token:
                git.gitToken=git_token
                db.session.commit()
                
            
            if git_link:
                git.repositoryURL=git_link
                db.session.commit()
                

        elif git_link and git_token:
            add_git=Git_Link(projectID = pID, gitToken = git_token, repositoryURL=git_link)
            db.session.add(add_git)
            db.session.commit()
            token=git_token
            url=git_link
        else:
            flash("Warning! Could not configure git settings. Ensure that you have entered both the link and the token", category='warning')

        # if int_deadline:
        #     if int_date:
        #         new_deadline=Deadline(projectID=pID,title=int_deadline,deadlineDate=int_date, achieved=0)
        #         db.session.add(new_deadline)
        #         db.session.commit()
        #     else:
        #         flash('You must add a deadline date alongside the title', category='error')

        if update_interval:
            project_details.updateInterval=update_interval
            db.session.commit() 
        
        
            

    return render_template("project_details.html",project_details=project_details, budget=budget, cost=cost, token=token, url = url)


