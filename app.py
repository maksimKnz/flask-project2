from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, RadioField
from wtforms.validators import InputRequired, Length
import random
import json
import os


app = Flask(__name__)
app.secret_key = 'Secret!'
hours = {"1-2": "1-2 часа", "3-5": "3-5 часов", "5-7": "5-7 часов", "7-10": "7-10 часов"}
days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": "Суббота", "sun": "Воскресенье"}
week = {'sun': 'sunday', 'mon': 'monday', 'tue': 'tuesday', 'wed': 'wednesday', 'thu': 'thursday', 'fri': 'friday', 'sat': 'saturday'}


class BookingForm(FlaskForm):
    clientName = StringField('Вас зовут', [InputRequired()])
    clientPhone = StringField('Ваш телефон', [InputRequired()])
    clientWeekday = HiddenField()
    clientTime = HiddenField()
    clientTeacher = HiddenField()


# эта функция для добавления цели
def add_goal(id_list, new_goal_eng, new_goal_ru, new_goal_pic):
    data = get_data()
    data['goals'].update({new_goal_eng: new_goal_ru})
    data['emodji'].update({new_goal_eng: new_goal_pic})
    for id in id_list:
        if new_goal_eng not in data['teachers'][id]['goals']:
            data['teachers'][id]['goals'].append(new_goal_eng)
    out = {'goals': data['goals'], 'teachers': data['teachers'], 'emodji': data['emodji']}
    with open("data.txt", "w") as f:
        json.dump(out, f)


def get_data():
    with open("data.txt", "r") as d:
        data = json.load(d)
    return data


class RequestForm(FlaskForm):
    data = get_data()
    clientName = StringField('Вас зовут', [InputRequired(), Length(min=2, message='Пожалуйста укажите ваше имя')])
    clientPhone = StringField('Ваш телефон', [InputRequired(), Length(min=5, message='Пожалуйста укажите номер телефона')])
    time = RadioField('Сколько времени есть?', choices=[(key, value) for key, value in hours.items()])
    goals = RadioField('Какая цель занятий?', choices=[(key, value) for key, value in data['goals'].items()])


def convert_day(day):
    for key, value in week.items():
        if value == day:
            return key


def add_callback(name, phone, goal, time):
    records = []
    if os.path.isfile('request.json'):
        with open('request.json', 'r') as r:
            records = json.load(r)
    records.append({'name': name, 'phone': phone, 'goal': goal, 'time': time})
    with open('request.json', 'w') as w:
        json.dump(records, w)


def add_record(name, phone, teacher_id, day, time):
    records = []
    if os.path.isfile('booking.json'):
        with open('booking.json', 'r') as r:
            records = json.load(r)
    records.append({'name': name, 'phone': phone, 'teacher': teacher_id, 'weekday': day, 'time': time})
    with open('booking.json', 'w') as w:
        json.dump(records, w)


@app.route('/')
def main():
    #add_goal((8, 9, 10, 11), 'programming', 'Для программирования', '🖥') #<- Так добавлял цель
    data = get_data()
    random_teachers_ids = []
    while len(random_teachers_ids) < 6:
        i = random.randint(0, len(data['teachers'])-1)
        if i not in random_teachers_ids:
            random_teachers_ids.append(i)
    return render_template('index.html', teachers=data['teachers'], ids=random_teachers_ids, pic=data['emodji'], goals=data['goals'])


@app.route('/goals/<goal>')
def show_goals(goal):
    data = get_data()
    sorted_list = []
    for teacher in data['teachers']:
        if goal in teacher['goals']:
            sorted_list.append(teacher)
    return render_template("goal.html", teachers=sorted_list, goals=data['goals'], goal=goal, pic=data['emodji'])


@app.route('/profiles/<int:teacher_id>/')
def show_profile(teacher_id):
    data = get_data()

    return render_template("profile.html", teacher=data['teachers'][teacher_id], goals=data['goals'], days=days, week=week)


@app.route('/request/')
def make_request():
    form = RequestForm()
    return render_template("request.html", form=form)


@app.route('/request_done/', methods=['POST'])
def request_done():
    form = RequestForm()
    data = get_data()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.clientName.data
            phone = form.clientPhone.data
            goal = form.goals.data
            time = form.time.data
            add_callback(name, phone, goal, time)
            return render_template("request_done.html", name=name, phone=phone, goal=data['goals'].get(goal), time=hours.get(time))
        else:
            return render_template("request.html", form=form)
    else:
        return render_template("request.html")


@app.route('/booking/<int:teacher_id>/<day>/<time>/')
def booking(teacher_id, day, time):
    data = get_data()
    what_day = convert_day(day)
    time = time + ":00"
    form = BookingForm(clientTime=time, clientWeekday=what_day, clientTeacher=teacher_id)
    return render_template("booking.html", teacher=data['teachers'][teacher_id], day=what_day, time=time, days=days, form=form)


@app.route('/booking_done/', methods=['POST'])
def booking_save():
    form = BookingForm()
    if request.method == 'POST':
        name = form.clientName.data
        phone = form.clientPhone.data
        day = form.clientWeekday.data
        time = form.clientTime.data
        teacher_id = form.clientTeacher.data
        add_record(name, phone, teacher_id, day, time)
        return render_template("booking_done.html", name=name, phone=phone, day=days.get(day), time=time, teacher_id=teacher_id)
    else:
        return render_template("index.html")


@app.errorhandler(404)
def render_not_found(err):
    return "Ничего не нашлось! Вот неудача, отправляйтесь на главную!", 404, err


@app.errorhandler(500)
def render_server_error(err):
    return "Что-то не так, но мы все починим", 500, err


if __name__ == '__main__':
    app.run()
