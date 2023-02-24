from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, current_user
from .models import Project, Git_Link, Hard_Metrics
from . import db
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

@views.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user)

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
            project=Project(managerID=managerid, dateCreated=today_unix, title=title, dateLastSurveyed=0,dateLastRiskCalculation=today_unix,updateInterval=0)
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


@views.route('/view')
@login_required
def view():
    return render_template("view.html", user=current_user)