from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_security import RoleMixin

db = SQLAlchemy()


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.user_id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.role_id'))
)


class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default=False)
    roles = db.relationship('Role', secondary=roles_users, 
                            backref=db.backref('users', lazy='dynamic'))


    def get_id(self):
        return self.id


class Role(db.Model, RoleMixin):
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)


# class Association(db.Model):
#     venue_id = db.Column(db.Integer(), db.ForeignKey("venue.venue_id"), primary_key = "True")
#     show_id = db.Column(db.Integer(), db.ForeignKey("show.show_id"), primary_key = "True")


class Venue(db.Model):
    venue_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    place = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    
    shows = db.relationship("Show", backref = "available", cascade="delete")


class Show(db.Model):
    show_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    language = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, nullable=False)
    timing = db.Column(db.String, nullable=False)
    capacity = db.Column(db.String, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.venue_id'), nullable=False)
    # current_shows = db.relationship("Venue", secondary = "association", backref = "available", cascade="delete") #Showing_currently


class Bookings(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    show_id = db.Column(db.Integer, db.ForeignKey("show.show_id"))
    show_name = db.Column(db.String, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.venue_id"))
    venue_name = db.Column(db.String, nullable=False)
    num_tickets = db.Column(db.String, nullable=False)
    # amount = db.Column(db.String, nullable=False)
    # bookings = db.Relationship("User", backref="booked")
    user = db.relationship('User', backref='bookings', cascade='delete') #All bookings made by the user
    show = db.relationship('Show', backref='bookings', cascade='delete')
    venue = db.relationship('Venue', backref='bookings', cascade='delete')

