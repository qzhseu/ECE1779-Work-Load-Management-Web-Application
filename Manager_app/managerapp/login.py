from managerapp import app
from flask import render_template, flash, redirect, url_for, session, logging, request, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user
from managerapp.form import LoginForm

@app.route('/login',methods=['GET','POST'])
def login():
    if 'user' in session:
        logout()
    form = LoginForm()
    if form.validate_on_submit:
        #Get formfield
        username=form.username.data
        password=form.password.data
        if username and password is not None:
            if username != 'admin' or password != 'admin':
                flash("Your password is worng, please try again", 'danger')
            else:
                session['user'] = 'admin'
                return redirect(url_for('home'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))