from flask import render_template, url_for, flash, redirect, request
from app import app
from flask_login import login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, SubmissionForm
from json_modules import User, Problem, Submission
from werkzeug.security import check_password_hash

@app.route("/")
@app.route("/home")
def home():
    problems = Problem.get_all()
    return render_template('home.html', problems=problems)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user and check_password_hash(user['password'], form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/problem/<int:problem_id>")
def problem(problem_id):
    problem = Problem.find_by_id(problem_id)
    if not problem:
        return redirect(url_for('home'))
    form = SubmissionForm()
    return render_template('problem.html', title=problem['title'], problem=problem, form=form)

@app.route("/submit/<int:problem_id>", methods=['POST'])
@login_required
def submit(problem_id):
    problem = Problem.find_by_id(problem_id)
    if not problem:
        return redirect(url_for('home'))
    form = SubmissionForm()
    if form.validate_on_submit():
        Submission.create(code=form.code.data, result="Pending", user_id=current_user.id, problem_id=problem_id)
        # Here you would send the code to be run in a Docker container and get the result
        # For now, we just set it to "Success"
        flash('Your code has been submitted!', 'success')
        return redirect(url_for('problem', problem_id=problem_id))
    return render_template('problem.html', title=problem['title'], problem=problem, form=form)
