from ast import Sub
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DecimalField
from wtforms.validators import DataRequired
import pandas as pd

class GetNumberofAxles(FlaskForm):
    axles = SelectField(choices = [x for x in range(2, 16)], label = 'Number of axles', validators = [DataRequired()])
    submit = SubmitField('Submit')

class GetAxleLoads(FlaskForm):
    axle1 = DecimalField('Axle 1', validators = [DataRequired()])
    axle2 = DecimalField('Axle 2', validators = [DataRequired()])
    axle3 = DecimalField('Axle 3', validators = [DataRequired()])
    axle4 = DecimalField('Axle 4', validators = [DataRequired()])
    axle5 = DecimalField('Axle 5', validators = [DataRequired()])
    axle6 = DecimalField('Axle 6', validators = [DataRequired()])
    axle7 = DecimalField('Axle 7', validators = [DataRequired()])
    axle8 = DecimalField('Axle 8', validators = [DataRequired()])
    axle9 = DecimalField('Axle 9', validators = [DataRequired()])
    axle10 = DecimalField('Axle 10', validators = [DataRequired()])
    axle11 = DecimalField('Axle 11', validators = [DataRequired()])
    axle12 = DecimalField('Axle 12', validators = [DataRequired()])
    axle13 = DecimalField('Axle 13', validators = [DataRequired()])
    axle14 = DecimalField('Axle 14', validators = [DataRequired()])
    axle15 = DecimalField('Axle 15', validators = [DataRequired()])
    submit = SubmitField('Submit')

class GetAxleSpacing(FlaskForm):
    axle1_2 = DecimalField('Axle 1 and 2', validators = [DataRequired()])
    axle2_3 = DecimalField('Axle 2 and 3', validators = [DataRequired()])
    axle3_4 = DecimalField('Axle 3 and 4', validators = [DataRequired()])
    axle4_5 = DecimalField('Axle 4 and 5', validators = [DataRequired()])
    axle5_6 = DecimalField('Axle 5 and 6', validators = [DataRequired()])
    axle6_7 = DecimalField('Axle 6 and 7', validators = [DataRequired()])
    axle7_8 = DecimalField('Axle 7 and 8', validators = [DataRequired()])
    axle8_9 = DecimalField('Axle 8 and 9', validators = [DataRequired()])
    axle9_9 = DecimalField('Axle 8 and 9', validators = [DataRequired()])
    axle9_10 = DecimalField('Axle 9 and 10', validators = [DataRequired()])
    axle10_11 = DecimalField('Axle 10 and 11', validators = [DataRequired()])
    axle11_12 = DecimalField('Axle 11 and 12', validators = [DataRequired()])
    axle12_13 = DecimalField('Axle 12 and 13', validators = [DataRequired()])
    axle13_14 = DecimalField('Axle 13 and 14', validators = [DataRequired()])
    axle14_15 = DecimalField('Axle 14 and 15', validators = [DataRequired()])
    submit = SubmitField('Submit')

def CleanDictionaries(axleLoads, axleSpacing):

    truck = {"Axle number": [x for x in range(1, len(axleLoads))], "Load": [], "Axle spacing": [0]}

    for key, value in axleLoads.items():
        if key != "submit":
            truck['Load'].append(value)

    for key, value in axleSpacing.items():
        if key != "submit":
            truck['Axle spacing'].append(value)

    return truck