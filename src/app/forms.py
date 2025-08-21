from flask_wtf import FlaskForm
from flask_wtf import CSRFProtect
from flask_wtf.form import _Auto
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import validators
from wtforms import IntegerField
from wtforms import DateField
from wtforms import TimeField
from wtforms import MonthField
from wtforms import DateTimeField
from wtforms.validators import DataRequired
from wtforms.fields.datetime import DateTimeLocalField
from datetime import datetime


class SignUpForm(FlaskForm):
    id = StringField(
        'Username',
        validators=[DataRequired()]
        )
    passwd = PasswordField(
        'Password',
        validators=[DataRequired()]
        )
    passwd_confirm = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
        )
    submit = SubmitField('Confirm')


class LoginForm(FlaskForm):
    id = StringField('Username',
                     validators=[DataRequired()]
                     )
    passwd = PasswordField('Password',
                           validators=[DataRequired()]
                           )
    submit = SubmitField('Confirm')


class CreateEvent(FlaskForm):
    title = StringField(
        'Title of Event:',
        validators=[DataRequired()]
        )
    start_time = DateTimeLocalField('Start',
                                    format='%Y-%m-%dT%H:%M',
                                    validators=[DataRequired()]
                                    )
    end_time = DateTimeLocalField('Start',
                                  format='%Y-%m-%dT%H:%M',
                                  validators=[DataRequired()]
                                  )
    notes = StringField('Notes:')
    submit = SubmitField('Confirm Changes')


class EditForm(FlaskForm):
    new_title = StringField('Title')
    new_start_time_and_date = DateTimeLocalField('Start',
                                                 format='%Y-%m-%dT%H:%M',
                                                 validators=[DataRequired()]
                                                 )
    new_end_time_and_date = DateTimeLocalField('Start',
                                               format='%Y-%m-%dT%H:%M',
                                               validators=[DataRequired()]
                                               )
    new_event_notes = StringField('Notes')
    submit = SubmitField('Confirm')


class CreateTask(FlaskForm):
    title = StringField('Title of Event:',
                        validators=[DataRequired()]
                        )
    start_time = DateTimeLocalField('Start',
                                    format='%Y-%m-%dT%H:%M',
                                    validators=[DataRequired()]
                                    )
    notes = StringField('Notes:')
    submit = SubmitField('Confirm Changes')


class EditTaskForm(FlaskForm):
    new_title = StringField('Title')
    new_start_time_and_date = DateTimeLocalField('Start',
                                                 format='%Y-%m-%dT%H:%M',
                                                 validators=[DataRequired()]
                                                 )
    new_task_notes = StringField('Notes')
    submit = SubmitField('Confirm')


class SearchForm(FlaskForm):
    date = DateTimeLocalField('Start',
                              format='%Y-%m-%dT%H:%M',
                              validators=[DataRequired()]
                              )
    EVENT_TASK = [('a', 'Any'),
                  ('e', 'Event'),
                  ('t', 'Task')
                  ]
    event_or_task = SelectField('event or task',
                                choices=EVENT_TASK)
    submit = SubmitField('Confirm')
