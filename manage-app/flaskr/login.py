from flask import render_template, request, flash, redirect, url_for, session
from flaskr import app
from flaskr import forms
import traceback

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if 'user' in session:
            logout()

        form = forms.LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            if username != 'admin' or password != 'admin':
                flash("Username or Password does not exist")
            else:
                session['user']='admin'
                return redirect(url_for('home'))

        return render_template('login.html', form=form)

    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        return render_template('error.html', msg='something goes wrong~')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))