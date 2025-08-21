from app import app
from app import db
from app import load_user
from app.models import *
from app.forms import *
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
import uuid
import datetime
import time
import bcrypt
import pendulum
from .time_tester import DatetimeSimulator
from app import cache
import calendar


def simulate():
    print("time simulated")
    global simulated_time
    simulated_time = DatetimeSimulator(2024, 5, 9, 17, 40, 0)
    simulated_time.add_time(0)
    simulated_time = simulated_time.get_simulated_datetime()


def todays_date():
    print('date fetched')
    date = datetime.datetime.today()
    print(str(date))
    return date


# don't call this unless the page has @login_required
def user_sorted_calendar_objects():
    objs = CalendarObject.query.filter_by(user_id=current_user.id).all()
    return sorted(objs, key=lambda x: x.start_time)


# pass current_user into this function.
# only call this function on @login_required routes
def check_tasks_and_reschedule(user: User):
    all_tasks = Task.query.filter_by(user_id=user.id).all()
    current_time = time.mktime(simulated_time.timetuple())
    for task in all_tasks:
        task_start = time.mktime(task.start_time.timetuple())
        # problem: what if it is multiple days behind?
        if task_start <= current_time:
            print("task before" + str(task.start_time))
            task.start_time += datetime.timedelta(hours=24)
            print("task after" + str(task.start_time))
            db.session.add(task)
            db.session.commit()


def get_offset_via_pfm():
    today = pendulum.now()
    print(today.start_of('month'))
    today = today.start_of('month').weekday()
    today = today + 1
    if today == 7:
        today = 0
    return today


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/users/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if form.passwd.data == form.passwd_confirm.data:
            # using bcrypt, we create the "salted" hashed password.
            hash_password = bcrypt.hashpw(
                form.passwd.data.encode('utf-8'),
                bcrypt.gensalt()
                )
            new_user = User()
            new_user.id = form.id.data
            new_user.password = hash_password
            db.session.add(new_user)
            db.session.commit()

            return render_template('index.html')
    return render_template('signup.html', form=form)


@app.route('/users/signout', methods=['GET', 'POST'])
def signout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/users/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.id.data).first()
        if user:
            if bcrypt.checkpw(form.passwd.data.encode('utf-8'), user.password):
                login_user(user)
                print("week page")
                return render_template('week.html',
                                       today=simulated_time.weekday(),
                                       events=user_sorted_calendar_objects(),
                                       current_time=simulated_time,
                                       wk_offset=pendulum.now().week_of_month,
                                       offset=get_offset_via_pfm()
                                       )

    else:
        return render_template('login.html', form=form)


# change int to a DateTime or string representation of a DateTime Class.
@app.route('/users/day/<int:day>', methods=['GET', 'POST'])
@login_required
def day(day):
    # days = [
    #     'Monday',
    #     'Tuesday',
    #     'Wednesday',
    #     'Thursday',
    #     'Friday',
    #     'Saturday',
    #     'Sunday'
    # ]
    date = simulated_time
    date = datetime.datetime(year=date.year, month=date.month, day=day)
    # day = day % 7
    # match day:
    #     case 0:
    #         weekday = "Monday"
    #     case 1:
    #         weekday = "Tuesday"
    #     case 2:
    #         weekday = "Wednesday"
    #     case 3:
    #         weekday = "Thursday"
    #     case 4:
    #         weekday = "Friday"
    #     case 5:
    #         weekday = "Saturday"
    #     case 6:
    #         weekday = "Sunday"

    day_events_list = []
    c_objs = CalendarObject.query.filter_by(user_id=current_user.id).all()
    for obj in c_objs:
        print(obj.start_time.day)
        # hange month/year too
        if obj.start_time.day == day:
            print("appending " + str(obj.type) + " for day")
            day_events_list.append(obj)
    day_events_list = sorted(day_events_list, key=lambda x: x.start_time)
    for i in day_events_list:
        print(i.start_time)
    return render_template('day.html',
                           date=date.strftime("%D"),
                           events=day_events_list
                           )


@app.route('/users/week', methods=['GET', 'POST'])
@login_required
def week():
    # description for weekday() is actually helpful
    check_tasks_and_reschedule(current_user)
    get_offset_via_pfm()
    return render_template('week.html',
                           today=simulated_time.weekday(),
                           events=user_sorted_calendar_objects(),
                           current_time=simulated_time,
                           wk_offset=pendulum.now().week_of_month,
                           offset=get_offset_via_pfm()
                           )


@app.route('/users/month', methods=['GET', 'POST'])
@login_required
def month():
    date = simulated_time
    year = date.year
    month = date.month
    weekday_days = calendar.monthrange(year, month)
    start_day, days_in_month = weekday_days
    today = pendulum.now()
    print(today.start_of('month'))
    today = today.start_of('month').weekday()
    today = today + 1
    if today == 7:
        today = 0
    print(today)
    return render_template('month.html',
                           start_day=int(start_day),
                           days_in_month=int(days_in_month),
                           offset=today
                           )


@app.route('/users/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    error_message = ""
    form = CreateEvent()
    if form.validate_on_submit():
        check_tasks_and_reschedule(current_user)
        form_start_time_int = time.mktime(form.start_time.data.timetuple())
        form_end_time_int = time.mktime(form.end_time.data.timetuple())
        if form_start_time_int < form_end_time_int:
            new_event = Event(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                title=form.title.data,
                type=CalendarObjectType.event,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                date=datetime.datetime.now(),
                notes=form.notes.data
            )

            db.session.add(new_event)
            db.session.commit()
        if form_start_time_int >= form_end_time_int:
            error_message = "Invalid date range!"
            return render_template('addevent.html',
                                   error=error_message,
                                   form=form
                                   )
        return render_template('week.html',
                               today=simulated_time.weekday(),
                               events=user_sorted_calendar_objects(),
                               current_time=simulated_time,
                               wk_offset=pendulum.now().week_of_month,
                               offset=get_offset_via_pfm()
                               )
    else:
        print("form isn't valid" + str(form.errors))
    return render_template('addevent.html', error=error_message, form=form)


@app.route('/users/view_event', methods=['GET', 'POST'])
@login_required
def edit_event_view():
    return render_template('viewevent.html', error="")


@app.route('/users/edit_event/<string:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    form = EditForm()
    event = Event.query.filter_by(id=event_id).one_or_none()
    print(type(form.new_start_time_and_date.data))
    if form.validate_on_submit() and event is not None:
        form_start_time_int = time.mktime(form.start_time.data.timetuple())
        form_end_time_int = time.mktime(form.start_time.data.timetuple())
        if form_start_time_int < form_end_time_int:
            event.start_time = form.new_start_time_and_date.data
            event.end_time = form.new_end_time_and_date.data
            if form.new_event_notes.data.strip() != "":
                event.notes = form.new_event_notes.data
            if form.new_title.data.strip() != event.title.strip():
                event.title = form.new_title.data
        if form_start_time_int >= form_end_time_int:
            error_message = "Invalid date range!"
            return render_template('editevent.html',
                                   error=error_message,
                                   form=form
                                   )

        db.session.add(event)
        db.session.commit()

        return render_template('week.html',
                               today=simulated_time.weekday(),
                               events=user_sorted_calendar_objects(),
                               current_time=simulated_time,
                               wk_offset=pendulum.now().week_of_month,
                               offset=get_offset_via_pfm()
                               )
    else:
        print("form not valid")
    return render_template('editevent.html',
                           form=form,
                           event_id=event_id,
                           event=event
                           )


@app.route('/users/delete_event/<string:event_id>', methods=['GET', 'POST'])
@login_required
def delete_event(event_id):
    event_to_delete = Event.query.filter_by(id=event_id).one_or_none()
    if event_to_delete:
        db.session.delete(event_to_delete)
        db.session.commit()
        check_tasks_and_reschedule(current_user)
    return render_template('week.html',
                           today=simulated_time.weekday(),
                           events=user_sorted_calendar_objects(),
                           current_time=simulated_time,
                           wk_offset=pendulum.now().week_of_month,
                           offset=get_offset_via_pfm()
                           )


@app.route('/user/delete_task/<string:task_id>', methods=['GET', 'POST'])
@login_required
def delete_task(task_id):
    task_to_delete = Task.query.filter_by(id=task_id).one_or_none()
    if task_to_delete:
        db.session.delete(task_to_delete)
        db.session.commit()
        check_tasks_and_reschedule(current_user)
    return render_template('week.html',
                           today=simulated_time.weekday(),
                           events=user_sorted_calendar_objects(),
                           current_time=simulated_time,
                           wk_offset=pendulum.now().week_of_month,
                           offset=get_offset_via_pfm()
                           )


@app.route('/users/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    error_message = ""
    form = CreateTask()
    if form.validate_on_submit():
        # check_tasks_and_reschedule(current_user)
        form_start_time_int = time.mktime(form.start_time.data.timetuple())
        current_time_int = time.mktime(datetime.datetime.now().timetuple())
        if form_start_time_int > current_time_int:
            new_task = Task()
            new_task.type = CalendarObjectType.task
            new_task.id = str(uuid.uuid4())
            new_task.is_complete = False
            new_task.title = form.title.data
            new_task.date = datetime.datetime.now()
            new_task.start_time = form.start_time.data
            new_task.notes = form.notes.data
            new_task.user_id = current_user.id

            db.session.add(new_task)
            db.session.commit()
        if form_start_time_int <= current_time_int:
            error_message = "Invalid Time!"
            return render_template('addtask.html',
                                   error=error_message,
                                   form=form)
        return render_template('week.html',
                               today=simulated_time.weekday(),
                               events=user_sorted_calendar_objects(),
                               current_time=simulated_time,
                               wk_offset=pendulum.now().week_of_month,
                               offset=get_offset_via_pfm()
                               )
    else:
        print("form isn't valid" + str(form.errors))
    return render_template('addtask.html',
                           error=error_message,
                           form=form
                           )


@app.route('/users/edit_task/<string:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    form = EditTaskForm()
    task = CalendarObject.query.filter_by(id=task_id).one_or_none()
    print(type(form.new_start_time_and_date.data))
    if form.validate_on_submit() and task is not None:
        formtime = form.new_start_time_and_date.data
        form_start_time_int = time.mktime(formtime.timetuple())
        current_time_int = time.mktime(datetime.datetime.now().timetuple())
        print(str(form_start_time_int) + "   " + str(current_time_int))
        if form_start_time_int > current_time_int:
            task.start_time = formtime
            if form.new_task_notes.data.strip() != "":
                task.notes = form.new_task_notes.data
            if form.new_title.data.strip() != task.title.strip():
                task.title = form.new_title.data
        if form_start_time_int <= current_time_int:
            print("form not valid")
            error_message = "Invalid date range!"
            return render_template('edittask.html',
                                   form=form,
                                   error=error_message,
                                   task=task,
                                   task_id=task_id
                                   )

        db.session.add(task)
        db.session.commit()

        return render_template('week.html',
                               today=simulated_time.weekday(),
                               events=user_sorted_calendar_objects(),
                               current_time=simulated_time,
                               wk_offset=pendulum.now().week_of_month,
                               offset=get_offset_via_pfm()
                               )
    else:
        print("form not valid")
    return render_template('edittask.html',
                           form=form,
                           task=task,
                           task_id=task_id
                           )


@app.route('/users/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        check_tasks_and_reschedule(current_user)
        if form.date.data is not None:
            requested_time = time.mktime(form.date.data.timetuple())
            selections = []
            if form.event_or_task.data == 'a':
                selections = user_sorted_calendar_objects()
            user_id = current_user.id
            if form.event_or_task.data == 't':
                selections = Task.query.filter_by(user_id=user_id).all()
                selections = sorted(selections, key=lambda x: x.start_time)
            if form.event_or_task.data == 'e':
                selections = Event.query.filter_by(user_id=user_id).all()
                selections = sorted(selections, key=lambda x: x.start_time)
            requested_list = []
            for et in selections:
                start_time = time.mktime(et.start_time.timetuple())
                within_24 = time.mktime(
                    (form.date.data + datetime.timedelta(days=1)).timetuple()
                    )
                if start_time >= requested_time and start_time <= within_24:
                    requested_list.append(et)
        return render_template('search.html',
                               form=form,
                               events=requested_list
                               )
    return render_template('search.html',
                           form=form
                           )
