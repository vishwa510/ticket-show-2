from flask import Flask, redirect, render_template, jsonify, request
from flask_security import Security, SQLAlchemyUserDatastore, login_required, roles_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from flask_restful import Api
from models import *
from api import User_api, Venue_api, Show_api, Bookings_api
from flask_mail import Mail, Message
from celery.schedules import crontab
from mail import configure_mail
from worker import celery
import celerytask
from cacheinst import cache


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.sqlite3"
api = Api(app)
app.config['SECRET_KEY'] = "SUPER SECRET"

app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)


db.init_app(app)
cache.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
app.app_context().push()


api.add_resource(User_api, '/user', '/user/<string:email>')
api.add_resource(Venue_api, '/venue/<int:venue_id>', '/venue')
api.add_resource(Show_api, '/show/<int:venue_id>',
                 '/show/<int:venue_id>/<int:show_id>')
api.add_resource(Bookings_api, '/booking/<int:user_id>', '/booking/<int:user_id>/<int:venue_id>/<int:show_id>')

configure_mail(
    app,
    mail_server='smtp.office365.com',
    mail_port=587,
    mail_use_tls=True,
    mail_username='mad2project@outlook.com',
    # mail_default_sender='mad2project@outlook.com',
    mail_password='secret10',
    mail_use_ssl=False
)

@app.route("/")
def home():
    return render_template("home.html")


@app.route('/userLogin', methods=["POST"])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    res = User.query.filter_by(email=email).first()
    if res and res.password == password:
        token = create_access_token(
            identity=res.user_id, expires_delta=False)
        response = {
            'message': 'Login successful',
            'user_id': res.user_id,
            'token': token,
            'role': res.role
        }
        headers = {'Authorization': f'Bearer {token}'}
        return response, 200, headers
    else:
        return {'message': 'Invalid credentials'}, 401


@app.route('/logout', methods=["POST"])
@jwt_required()
def logout():
    # print('logged out', current_user)
    # headers = {'Authorization': f'Bearer {token}'}
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/mail')
def index():

    users = User.query.all()
    for user in users:
        msg=Message(subject='Hey',sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email] )
        mail.send(msg)
        print(user.email)


    return 'Message sent12'


@app.route('/export/daily')
def dailyreminder():
    celerytask.daily_reminder.delay()
    print('success')
    return jsonify('')


@app.route('/exportShow/<int:venue_id>/<int:show_id>/<int:user_id>')
def exportShow(venue_id, show_id, user_id):
    celerytask.exportShow.delay(venue_id, show_id, user_id)
    return jsonify('Task submitted')


@app.route('/exportVenue/<int:venue_id>/<int:user_id>')
def exportVenue(venue_id, user_id):
    celerytask.exportVenue.delay(venue_id, user_id)
    return jsonify('Task submitted')


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('search')

    res = Show.query.filter(Show.name.like('%' + query + '%')).all()
    res2 = Show.query.filter(Show.genre.like('%' + query + '%')).all()
    res3 = Venue.query.filter(Venue.city.like('%' + query + '%')).all()
    res4 = Venue.query.filter(Venue.place.like('%' + query + '%')).all()
    res5 = Venue.query.filter(Venue.name.like('%' + query + '%')).all()
    res6 = Show.query.filter(Show.language.like('%' + query + '%')).all()

    show = []
    venue=[]
    if len(res) > 0:
        for i in range(0, len(res)):
            show.append(res[i].name)
    elif len(res2) > 0:
        for i in range(0, len(res2)):
            show.append(res2[i].name)
    elif len(res3)>0:
        for i in range(0, len(res3)):
            venue.append(res3[i].name)
    elif len(res4)>0:
        for i in range(0, len(res4)):
            venue.append(res4[i].name)
    elif len(res5)>0:
        for i in range(0, len(res5)):
            venue.append(res5[i].name)
    elif len(res6)>0:
        for i in range(0, len(res6)):
            show.append(res6[i].name)
    else:
        return "Sorry, there were no matching results"

    if len(show) > 0:
        results = ', '.join(show)
    elif len(venue) > 0:
        results = ', '.join(venue)
    else:
        return "Sorry there were no matching results"

    return jsonify({'results': results})

if __name__ == "__main__":
    app.run(debug=True)