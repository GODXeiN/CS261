from flask import Blueprint,render_template,request, flash,redirect, url_for
from .models import Manager
from . import db
from flask_login import login_user, login_required, logout_user, current_user

from werkzeug.security import generate_password_hash, check_password_hash
# from password_strength import PasswordPolicy
# from password_strength import PasswordStats

auth = Blueprint('auth', __name__)

# policy=PasswordPolicy.from_names(length=0, uppercase=1, numbers=1, special=1)

@auth.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('pw1')
        user= Manager.query.filter_by(emailAddr=email).first()


        if user:
            if check_password_hash(user.hashedPW, password):
                flash('log in success', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password. Try again', category='error')
        else:
            flash('Email does not exist. Incorrect user', category='error')
    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        email=request.form.get('email')
        name=request.form.get('name')
        password1=request.form.get('pw1')
        password2=request.form.get('pw2')
        user= Manager.query.filter_by(emailAddr=email).first()
        if (password1==password2):
            if user:
                flash('This email is already being used. Try a different one', category='error')
            else:
                new_user=Manager(emailAddr=email, firstName=name, hashedPW=generate_password_hash(password1, method='sha256'))
                flash('Account created!', category='success')
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)

                return redirect(url_for('views.home'))
        else:
            flash('Your passwords do not match!')

    return render_template("signup.html")

@auth.route('/user', methods=['GET','POST'])
@login_required
def user():
    user=Manager.query.filter_by(managerID=current_user.managerID).first()

    if request.method=='POST':
        user.firstName=request.form["new_name"]
        db.session.commit()
        flash('name changed!', category='success')
        return redirect(url_for('views.home'))
    return render_template("user.html", user=user)