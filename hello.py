from flask import Flask, render_template, redirect, request, url_for, session
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
import webbrowser

# import from forms.py
from forms import GetNumberofAxles, GetAxleLoads, GetAxleSpacing, CleanDictionaries
from algorithm import ProduceMap

import pandas as pd
import json

# create a Flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "my secret key"

# create a route decorator
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/step1', methods=['GET', 'POST'])
def step1():
    form1 = GetNumberofAxles()
    if form1.is_submitted():
        result_dict = request.form.to_dict()
        messages = json.dumps(result_dict)
        session['form1'] = messages
        return redirect(url_for("step2"))
    return render_template("index.html", form1 = form1)

@app.route('/step2', methods=['GET', 'POST'])
def step2():
    # load the "number of axles" form
    messages = session['form1']
    result1 = json.loads(messages)

    form2 = GetAxleLoads()
    if form2.is_submitted():
        result_dict = request.form.to_dict()
        messages = json.dumps(result_dict)
        session['form2'] = messages
        return redirect(url_for("step3"))
    return render_template("calculator2.html", result = result1, form2 = form2)

@app.route('/step3', methods=['GET', 'POST'])
def step3():
    # load the "number of axles" form
    message1 = session['form1']
    result1 = json.loads(message1)

    # load the "axle loads" form
    message2 = session['form2']
    result2 = json.loads(message2)

    form3 = GetAxleSpacing()
    if form3.is_submitted():
        result_dict = request.form.to_dict()
        messages = json.dumps(result_dict)
        session['form3'] = messages
        return redirect(url_for("step4"))
    return render_template("calculator3.html", result1 = result1, result2 = result2, form3 = form3)

@app.route('/step4', methods=['GET', 'POST'])
def step4():
    # load the "number of axles" form
    message1 = session['form1']
    result1 = json.loads(message1)

    # load the "axle loads" form
    message2 = session['form2']
    result2 = json.loads(message2)

    # load the "axle spacing" form
    message3 = session['form3']
    result3 = json.loads(message3)

    truck = CleanDictionaries(result2, result3)

    map = ProduceMap(truck, "static/inputs/bridge_data.csv", "static/inputs/coordinate.txt", "static/inputs/route.yaml")
    
    return render_template("calculator4.html", result1 = result1, 
                                                result2 = result2, 
                                                result3 = result3, 
                                                truck = truck,
                                                map = map)

##### Create custom error pages #####

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500