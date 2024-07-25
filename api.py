from flask import request, abort
from flask_restful import Resource, fields, marshal_with

from errors import NotFound, Invalid

from models import *


class User_api(Resource):

    output = {"user_id": fields.Integer, "email": fields.String,
              "password": fields.String}

    @marshal_with(output)
    def get(self, email: str): #To filter the user with the given email

        res = User.query.filter_by(email=email).first()

        # Checking whether user record is present
        if res is None:
            raise NotFound(status_code=404, error_message="No user found for the given email")

        return res, 200

    @marshal_with(output)
    def put(self, email: str): #To edit the user data for the email provided

        res = User.query.filter_by(email=email).first()

        # Checking whether user record is present
        if res is None:
            raise NotFound(status_code=404, error_message="No user found for the given email")

        res.password = request.get_json().get("password")

        # Input data checking
        if res.password is None or type(res.password) != str or len(res.password) == 0:
            raise Invalid(status_code=400, error_code="USER002",
                             error_message="Password field cannot be field. Password should be a valid text")

        return res, 202


    def delete(self, email: str):  #To delete the user for the given email

        res = User.query.filter_by(email=email).first()

        # Checking whether user record is present
        if res is None:
            raise NotFound(status_code=404, error_message="No user found for the given email")

        db.session.delete(res)
        db.session.commit()
        return '', 200


    @marshal_with(output)
    def post(self):  #To create a new User

        form = request.get_json()
        res = User(email=form.get("email"),
                   password=form.get("password"),
                   role = "user")

        # Input data checking
        if res.email is None or type(res.email) != str or len(res.email) == 0:
            raise Invalid(status_code=400, error_code="USER001",
                             error_message="Email is required and must be in text format.")
        if res.password is None or type(res.password) != str or len(res.password) == 0:
            raise Invalid(status_code=400, error_code="USER002",
                             error_message="Password is required and must be in string format.")

        # Checking whether a user record with same username is present
        if User.query.filter_by(email=res.email).first():
            raise NotFound(status_code=409, error_message="User already exists for the given information")

        db.session.add(res)
        db.session.commit()
        return res, 201

    
class Venue_api(Resource):

    output = {"venue_id": fields.Integer, "name": fields.String,
              "place": fields.String, "city": fields.String}

    @marshal_with(output)
    def get(self):

        res = Venue.query.all()

        # Checking whether user record is present
        if res is None:
            raise NotFound(status_code=404, error_message="No venue found for the given venue_id")

        return res, 200

    
    @marshal_with(output)
    def put(self, venue_id: int):

        res = Venue.query.filter_by(venue_id=venue_id).first()

        # Checking whether user record is present
        if res is None:
            raise NotFound(status_code=404, error_message="No venue found for the given venue_id")

        res.place = request.get_json().get("place")
        res.city = request.get_json().get("city")


        if res.place is None or type(res.place) != str or len(res.place) == 0:
            raise Invalid(status_code=400, error_code="Venue02", error_message="Venue place must be entered and should be a text")

        if res.city is None or type(res.city) != str or len(res.city) == 0:
            raise Invalid(status_code=400, error_code="Venue03", error_message="Venue city must be entered and should be a text")


        db.session.commit()
        return res, 202


    def delete(self, venue_id: int):
        
        res = Venue.query.filter_by(venue_id=venue_id).first()

        # Checking whether user record is present
        if res is None:
            raise NotFound(status_code=404, error_message="No venue found for the given venue_id")

        db.session.delete(res)
        db.session.commit()
        return '', 200

    
    @marshal_with(output)
    def post(self): #To add a new Venue

        form = request.get_json()
        res = Venue(name=form.get("name"),
                   place=form.get("place"),
                   city=form.get("city"))

        # Input data checking
        if res.name is None or type(res.name) != str or len(res.name) == 0:
            raise Invalid(status_code=400, error_code="Venue02",
                             error_message="Venue name must be entered and should be a text")


        if res.place is None or type(res.place) != str or len(res.place) == 0:
            raise Invalid(status_code=400, error_code="Venue03",
                             error_message="Venue place must be entered and should be a text")

        if res.city is None or type(res.city) != str or len(res.city) == 0:
            raise Invalid(status_code=400, error_code="Venue04",
                             error_message="Venue city must be entered and should be a text")



        # Checking whether a venue record with same name and place is present
        if Venue.query.filter_by(name=res.name, place=res.place).first():
            raise NotFound(status_code=409, 
                            error_message="Venue already exists for the given information")

        db.session.add(res)
        db.session.commit()
        return res, 201


class Show_api(Resource):

    output = {"show_id": fields.Integer, "venue_id": fields.Integer,
                "language": fields.String, "name": fields.String,
                "genre": fields.String, "timing": fields.String,
                "capacity": fields.String}


    @marshal_with(output)
    def get(self, venue_id: int): #To fetch all the shows in the venue entered

        venue_res = Venue.query.filter_by(venue_id=venue_id).first()

        # Checking whether a venue with the given id is present
        if venue_res is None:
            raise NotFound(status_code=404, error_message="No venue found for the given venue_id")
            
        res = Show.query.filter_by(venue_id=venue_id).all()

        return res, 200

    
    @marshal_with(output)
    def put(self, venue_id: int, show_id: int): #To edit the show for the given venue id and show id

        res = Show.query.filter_by(show_id=show_id, venue_id=venue_id).first()

        # Checking whether a show record with the given venue_id and show_id is present
        if res is None:
            raise NotFound(status_code=404, error_message="No show found for the given venue_id")        

        res.name = request.get_json().get("name")
        res.language = request.get_json().get("language")
        res.genre = request.get_json().get("genre")
        res.timing = request.get_json().get("timing")
        res.capacity = request.get_json().get("capacity")

        # Input data checking
        if res.name is None or type(res.name) != str or len(res.name) == 0:
            raise Invalid(status_code=400, error_code="Show02",
                             error_message="Show name must be entered and should be a text")


        if res.language is None or type(res.language) != str or len(res.language) == 0:
            raise Invalid(status_code=400, error_code="Show03",
                             error_message="Show language must be entered and should be a text")

        if res.genre is None or type(res.genre) != str or len(res.genre) == 0:
            raise Invalid(status_code=400, error_code="Show04",
                             error_message="Show genre must be entered and should be a text")

        if res.timing is None or type(res.timing) != int or len(res.timing) == 0:
            raise Invalid(status_code=400, error_code="Show05", 
                            error_message="A valid Show timing must be entered")

        db.session.commit()
        return res, 202


    def delete(self, venue_id: int, show_id: int):

        res = Show.query.filter_by(venue_id=venue_id, show_id=show_id).first()

        # Checking whether a show record with the given venue_id and show_id is present
        if res is None:
            raise NotFound(status_code=404, error_message="No show found for the given venue_id and show_id")

        db.session.delete(res)
        db.session.commit()
        return '', 200


    @marshal_with(output)
    def post(self, venue_id):

        form = request.get_json()
        res = Show(name=form.get("name"),
                   language=form.get("language"),
                   genre=form.get("genre"),
                   timing=form.get("timing"),
                   venue_id=venue_id,
                   capacity=form.get("capacity"))

        # Input data checking
        if res.name is None or type(res.name) != str or len(res.name) == 0:
            raise Invalid(status_code=400, error_code="Show02",
                             error_message="Show name must be entered and should be a text")


        if res.language is None or type(res.language) != str or len(res.language) == 0:
            raise Invalid(status_code=400, error_code="Show03",
                             error_message="Show language must be entered and should be a text")

        if res.genre is None or type(res.genre) != str or len(res.genre) == 0:
            raise Invalid(status_code=400, error_code="Show04",
                             error_message="Show genre must be entered and should be a text")

        if res.timing is None or type(res.timing) != str or len(res.timing) == 0:
            raise Invalid(status_code=400, error_code="Sjow05", 
                            error_message="A valid show timing must be entered")
            
        if res.capacity is None or type(res.capacity) != str or len(res.capacity) == 0:
            raise Invalid(status_code=400, error_code="Show06", 
                            error_message="Show capacity must be entered")

        # Checking whether a show record with same details is present
        if Show.query.filter_by(name=res.name, language=res.language, timing=res.timing).first():
            raise NotFound(status_code=409, 
                            error_message="Show already exists for the given information")

        db.session.add(res)
        db.session.commit()
        return res, 201


class Bookings_api(Resource):

    output = {"book_id": fields.Integer, "user_id": fields.Integer,
                "show_id": fields.Integer, "show_name": fields.String, "num_tickets": fields.Integer,
                "venue_id": fields.Integer, "venue_name": fields.String}

    
    @marshal_with(output)
    def get(self, user_id: int): #Fetching all bookings made by a user

        user_res = User.query.filter_by(user_id=user_id).first()

        # Checking whether a user with the given id is present
        if user_res is None:
            raise NotFound(status_code=404, error_message="No user found for the given user_id")
            
        res = Bookings.query.filter_by(user_id=user_id).all()

        return res, 200


    @marshal_with(output)
    def post(self, user_id: int, venue_id, show_id):

        form = request.get_json()

        numbertickets = int(form.get("num_tickets"))
        capacitystr = Show.query.filter_by(show_id=show_id).first().capacity
        capacityint = int(capacitystr)

        booklist = Bookings.query.all()

        total_tickets = 0

        for i in range(0, len(booklist)):
            tickets = int(booklist[i].num_tickets)
            total_tickets = total_tickets + tickets

        remainingtkts = capacityint - total_tickets

        userid = form.get("user_id")
        venueid = form.get("venue_id")
        showid = form.get("show_id")

        venue_name = Venue.query.filter_by(venue_id = venue_id).first().name
        show_name = Show.query.filter_by(show_id = show_id).first().name

        if (numbertickets < remainingtkts and numbertickets < capacityint):
            res = Bookings(user_id=user_id,                   
                            venue_id=venue_id,
                            show_id=show_id,
                            num_tickets=form.get("num_tickets"),
                            venue_name = venue_name,
                            show_name = show_name)
        else:
            raise Invalid(status_code=400, error_code="Booking05",
                            error_message="The show is housefull. Please book another show")

        
        

        # Input data checking
        if res.user_id is None or type(res.user_id) != int:
            raise Invalid(status_code=400, error_code="Booking02",
                             error_message="Enter a valid user_id")


        if res.show_id is None or type(res.show_id) != int:
            raise Invalid(status_code=400, error_code="Booking03",
                             error_message="Enter a valid show_id")

        if res.num_tickets is None or type(res.num_tickets) != str:
            raise Invalid(status_code=400, error_code="Booking04",
                             error_message="Please enter the number of tickets you wish to book")
        
        


        db.session.add(res)
        db.session.commit()
        return res, 201


