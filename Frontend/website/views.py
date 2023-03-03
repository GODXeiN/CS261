from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, current_user
from .models import Project, Git_Link, Hard_Metrics, Worker, Deadline
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
        hmetrics = Hard_Metrics.query.filter_by(projectID = entry.projectID).first()
        if hmetrics.status == 0:
            ongoing.append((entry.title,hmetrics.budget,datetime.utcfromtimestamp(entry.dateCreated).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(hmetrics.deadline).strftime('%Y-%m-%d %H:%M:%S'), entry.projectID))
        else:
            finished.append((entry,hmetrics))
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
            project=Project(managerID=managerid, dateCreated=today_unix, title=title, dateLastSurveyed=today_unix,dateLastRiskCalculation=today_unix,updateInterval=0)
            db.session.add(project)
            db.session.commit()
            proj_id=project.get_id()

            hard_metrics=Hard_Metrics(proj_id, date=today, budget=budget, costToDate=0, deadline=unix_deadline, status=0)
            #0=ongoing, 1=Completed, 2=Failed
            db.session.add(hard_metrics)
            db.session.commit()
        else:
            flash('Something went wrong with your inputs')
    #Post on refresh page bug!!
    return render_template("create_project.html")

@views.route('/end_project', methods=['GET','POST'])
@login_required
def end_project():
    if session.get('pID') is None:
        return redirect("/home")
    
    pID = session['pID']
    projectName = Project.query.filter_by(projectID=pID).first().title

    return render_template("end_project.html")

@views.route('/view')
@login_required
def view():
    if session.get('pID') is None:
        return redirect("/home")
    pID = session['pID']
    projectName = Project.query.filter_by(projectID=pID).first().title
    return render_template("view.html", projectName=projectName)

@views.route('/faq')
@login_required
def faq():
    return render_template("faq.html")

@views.route('/suggestions')
@login_required
def suggestions():
    if session.get('pID') is None:
        return redirect("/home")
    pID = session['pID']
    projectName = Project.query.filter_by(projectID=pID).first().title
    return render_template("suggestions.html", projectName=projectName)

@views.route('/manage_devs', methods=['GET','POST'])
@login_required
def manage_devs():
    if session.get('pID') is None:
        return redirect("/home")
    
    if request.method=='POST':
        dev_email=request.form.get('dev_email')

        dev=Worker.query.filter_by(emailAddr=dev_email).first()
        new_dev=Worker(emailAddr=dev_email, experienceRank=None)
        if dev:
            flash('Developer already exists.', category='error')
            
            
        else:
            print(dev_email)
            db.session.add(new_dev)
            db.session.commit()
            flash('Developer added successfully.', category='success')


    devs=Worker.query.all()
    #going from the user page to manage dev page gets an error once you submit
    return render_template("manage_devs.html", devs=devs)

@views.route('/delete_dev/<id>')
def delete_dev(id):
    dev=Worker.query.filter_by(workerID=id).first()
    if dev:
        db.session.delete(dev)
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
    
    project_details=Project.query.filter_by(projectID=1).first()
    hard_metrics=Hard_Metrics.query.filter_by(projectID=1).first()
    old_deadline=Hard_Metrics.deadline
    git=Git_Link.query.filter_by(projectID=1).first()
    
    #here we must include the project-specific values. The following is generic as in project id is just 1
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

        

        if new_title:
            project_details.title=new_title
            db.session.commit()
            
        if new_budget:
            hard_metrics.budget=new_budget
            db.session.commit()
            budget=hard_metrics.budget
            cost=hard_metrics.costToDate
            if budget<cost:
                excess=(cost/budget)*100
                flash("Warning! Your project's current cost exceeds the budget by " + str(round(excess,2)) + "%.", category='warning')
            
        if new_deadline:
            date_time_obj = datetime.strptime(new_deadline, '%Y-%m-%d')
            unix_deadline=int(date_time_obj.timestamp())
            hard_metrics.deadline=unix_deadline
            db.session.commit()
            if old_deadline>unix_deadline:
                flash('Warning. The updated deadline is earlier than the last one!', category='warning')

        if git_token:
            git.gitToken=git_token
            db.session.commit()
        
        if git_link:
            git.repositoryURL=git_link
            db.session.commit()
        
        if int_deadline:
            if int_date:
                new_deadline=Deadline(projectID=1,title=int_deadline,deadlineDate=int_date, achieved=0)
                db.session.add(new_deadline)
                db.session.commit()
            else:
                flash('You must add a deadline date alongside the title', category='error')

        if update_interval:
            project_details.updateInterval=update_interval
            db.session.commit()
        
        if cost_to_date:
            hard_metrics.costToDate=cost_to_date
            db.session.commit()
            budget=hard_metrics.budget
            cost=hard_metrics.costToDate
            if budget<cost:
                excess=(cost/budget)*100
                flash("Warning! Your project's current cost exceeds the budget by " + str(round(excess,2)) + "%.", category='warning')
 

        # if not new_budget and not new_deadline and not new_title and not update_interval and not git_link and not git_token and not int_date and not int_deadline and not cost_to_date:
        #     flash('Please insert data in any of the fields before submitting', category='warning')
    return render_template("project_details.html",project_details=project_details, hard_metrics=hard_metrics)

