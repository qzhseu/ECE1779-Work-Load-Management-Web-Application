from flask import render_template
from flaskr import app

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', msg="404 error")

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', msg="500 error")