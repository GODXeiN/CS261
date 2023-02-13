from flask import Blueprint,render_template,request, flash,redirect, url_for
from .models import Manager
from . import db

from werkzeug.security import generate_password_hash, check_password_hash
# from password_strength import PasswordPolicy
# from password_strength import PasswordStats

auth = Blueprint('auth', __name__)

# policy=PasswordPolicy.from_names(length=0, uppercase=1, numbers=1, special=1)

@auth.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        name=request.form.get('name')
        password=request.form.get('pw')

        user= Manager.query.filter_by(emailAddr=email).first()
        if user:
            if check_password_hash(user.hashedPW, password):
                flash('log in success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password. Try again')
        else:
            flash('Email does not exist. Incorrect user')
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<p>logout</p>"

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
                flash('User already exists. Try a different email address')
            else:
                new_user=Manager(emailAddr=email, firstName=name, hashedPW=generate_password_hash(password1, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash('Account created!', category='success')
                return redirect(url_for('auth.login'))
        else:
            flash('Your passwords do not match!')

    return render_template("signup.html")