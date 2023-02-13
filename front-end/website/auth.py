from flask import Blueprint,render_template,request, flash
# from password_strength import PasswordPolicy
# from password_strength import PasswordStats

auth = Blueprint('auth', __name__)

# policy=PasswordPolicy.from_names(length=0, uppercase=1, numbers=1, special=1)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        name=request.form.get('name')
        password=request.form.get('pw')
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
        password2=request.form.get('ps2')
    return render_template("signup.html")