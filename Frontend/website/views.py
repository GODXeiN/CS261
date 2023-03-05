from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, current_user
from .models import Project, Git_Link, Hard_Metrics, Worker, Deadline, Works_On, End_Result, Survey_Response
from . import db
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

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
    tomorrow= today+timedelta(1)
    # tomorrow_unix=int(tomorrow.timestamp())
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
            #0=ongoing, 1=Completed, 2=Failed
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
        metricOne=request.form.get('questionOne')
        metricTwo=request.form.get('questionTwo')
        metricThree=request.form.get('questionThree')
        metricFour=request.form.get('questionFour')
        metricFive=request.form.get('questionFive')
        metricSix=request.form.get('questionSix')
        new_status=request.form.get('status')

        end = End_Result(projectID = pID, metricOne=metricOne, metricTwo=metricTwo, metricThree = metricThree, metricFour = metricFour, metricFive = metricFive, metricSix = metricSix)
        new_metrics = Hard_Metrics(projectID=pID, date=today_unix, budget=hm.budget, costToDate=hm.costToDate, deadline=hm.deadline,status=new_status)
        db.session.add(end)
        db.session.add(new_metrics)
        db.session.commit()

        return redirect("/view")

    return render_template("end_project.html", projectName=projectName)

@views.route('/view')
@login_required
def view():
    if session.get('pID') is None:
        return redirect("/home")
    
    finished = True

    if session.get('pID') is None:
        return redirect("/home")
    if Hard_Metrics.query.filter_by(projectID = session.get('pID')).order_by(Hard_Metrics.date.desc()).first().status != 0:
        finished = False
    
    pID = session['pID']
    projectName = Project.query.filter_by(projectID=pID).first().title
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
    projectName = Project.query.filter_by(projectID=pID).first().title
    return render_template("suggestions.html", projectName=projectName)

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

        new_dev=Worker(emailAddr=dev_email, experienceRank=None)
        db.session.add(new_dev)
        db.session.commit()
        new_worksOn=Works_On(projectID = session['pID'], workerID = Worker.query.filter_by(emailAddr=dev_email).order_by(Worker.workerID.desc()).first().workerID)
        db.session.add(new_worksOn)
        db.session.commit()
        flash('Developer added successfully.', category='success')


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
        worker.experienceRank = experience
        db.session.commit()
        return redirect(f'/survey/{psID}')

    
    return render_template("initial_survey.html")

@views.route('/survey/<projectID>', methods=['GET','POST'])
def survey(projectID):
    session.pop('psID', None)
    if session.get('wID') is None:
        return redirect("/home")
    
    today_unix=int(datetime.now().timestamp())

    last_submission = Survey_Response.query.filter_by(workerID = session['wID']).order_by(Survey_Response.date.desc()).first()
    interval = int(Project.query.filter_by(projectID = projectID).first().updateInterval) * 24 * 60 * 60
    lastSurveyed = int(Project.query.filter_by(projectID = projectID).first().dateLastSurveyed)

    if last_submission:
        if (last_submission.date + interval > lastSurveyed):
            flash('You have already filled in the survey for the given time interval', category='error')
            return redirect(f"/survey_auth/{projectID}")


    if request.method=='POST':
        metricOne = request.form.get('questionOne')
        metricTwo = request.form.get('questionTwo')
        metricThree = request.form.get('questionThree')
        metricFour = request.form.get('questionFour')
        survey = Survey_Response(projectID=projectID, workerID=session['wID'], date=today_unix, metricOne=metricOne, metricTwo=metricTwo, metricThree=metricThree, metricFour=metricFour)
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
    hard_metrics=Hard_Metrics.query.filter_by(projectID=pID).first()
    old_deadline=hard_metrics.deadline
    old_budget=hard_metrics.budget
    old_cost=hard_metrics.costToDate
    git=Git_Link.query.filter_by(projectID=pID).first()
    
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
        else:
            flash("Warning! Could not configure git settings. Ensure that you have entered both the link and the token", category='warning')

        if int_deadline:
            if int_date:
                new_deadline=Deadline(projectID=pID,title=int_deadline,deadlineDate=int_date, achieved=0)
                db.session.add(new_deadline)
                db.session.commit()
            else:
                flash('You must add a deadline date alongside the title', category='error')

        if update_interval:
            project_details.updateInterval=update_interval
            db.session.commit() 

    return render_template("project_details.html",project_details=project_details, hard_metrics=hard_metrics, token=token, url = url)


