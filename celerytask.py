import csv
import os
from datetime import date, datetime
from celery.schedules import crontab
from jinja2 import Template
from flask_mail import Message
from worker import celery
from models import *
from mail import send_email, configure_mail
from email.message import EmailMessage
from cacheinst import cache


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/1'),
        monthly_reminder.s(),
    )
    sender.add_periodic_task(
        crontab(minute='*/2'),
        daily_reminder.s(),
    )


@celery.task
def monthly_reminder():
    # with app.app_context():
    users = User.query.all()
    month = date.today().strftime("%B")
    venuelist = Venue.query.all()
        
    for user in users:

        username = user.email.split('@')[0]
        adminlist = User.query.filter_by(role="admin").first()
        bookings = Bookings.query.all()
        num_book = len(bookings)

        html_template = """
        <html>
        <body>
            <p>This is the monthly report generated for the month: {{month}}</p>
            <table class="table table-striped">
                <thead>
                    <tr>Venue name</tr>
                    <tr>Shows</tr>
                    <tr>Bookings</tr>
                </thead>
                <tbody>
                    {% for venue in venuelist %}
                    <tr>
                        <td> {{venue.name}} </td>
                        <td> {{venue.shows}} </td>
                        <td> {{venue.bookings}} </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """
        subject = "Important reminder"
        msg_template = Template(html_template)
        body = msg_template.render(month = month, venuelist = venuelist)
        recipients = [adminlist.email]
        reci1 = ','.join(recipients)

        print(reci1)


        send_email(to=recipients, subject=subject, msg = body)

    return {
        'status': 'success',
        'message': 'Email has been sent to all users',
    }


@celery.task
def daily_reminder():
    users = User.query.all()

    for user in users:
        if (len(user.bookings) == 0): #To send a daily reminder only if the user has not booked a ticket

            username = user.email.split('@')[0]

            html_template = """
            <html>
            <body>
                <p>Hi {{ username }} this is an email to notify you that new movies have been released and it is time to book show tickets</p>
            </body>
            </html>
            """
            subject = "Important reminder"
            msg_template = Template(html_template)
            body = msg_template.render(username=username)
            recipients = [user.email]
            reci1 = ','.join(recipients)

            print(reci1)
            send_email(to=recipients, subject=subject, msg = body)

    return {
        'status': 'success',
        'message': 'Email has been sent',
    }


@celery.task
@cache.memoize(timeout=30)
def exportShow(venue_id: int, show_id: int, user_id: int):
    show_data = Show.query.filter_by(show_id=show_id).first()
    bookings = len(show_data.bookings)
    venue_name = Venue.query.filter_by(venue_id=show_data.venue_id).first().name
    filepath = 'static/download/' + show_data.name + '.csv'

    user = User.query.filter_by(user_id=user_id).first()

    # Check if folder is not present then create one
    if not os.path.exists('static/download/'):
        os.mkdir(path='static/download/')

    html_template = """
    <html>
    <body>
        <h1>CSV file for the show: {{ show_name }}</h1>
        <p>Name of venue: {{ venue_name }}</p>
        <p>Number of bookings: {{ bookings }}</p>
    </body>
    </html>
    """

    # Create a Jinja2 Template object from the HTML template string
    msg_template = Template(html_template)

    # Create the csv file
    with open(file=filepath, mode='w') as file:
        csv_obj = csv.writer(file, delimiter=',')

        csv_obj.writerow(['Show id', 'Show Name', 'Venue name', "Total Bookings"])
        csv_obj.writerow([show_id, show_data.name, venue_name, bookings])

    subject = 'CSV file for ' + show_data.name
    body = msg_template.render(show_name=show_data.name, venue_name=venue_name, bookings=bookings)
    recipients = [user.email]
    reci1 = ','.join(recipients)

    print(reci1)
    send_email(to=recipients, subject=subject, msg = body, attachment=filepath)

    return 'success'


@celery.task
@cache.memoize(timeout=30)
def exportVenue(venue_id: int, user_id: int):
    venue_data = Venue.query.filter_by(venue_id=venue_id).first()
    bookings = len(venue_data.bookings)
    shows = len(venue_data.shows)
    filepath = 'static/download/' + venue_data.name + '.csv'

    user = User.query.filter_by(user_id=user_id).first()

    # Check if folder is not present then create one
    if not os.path.exists('static/download/'):
        os.mkdir(path='static/download/')

    html_template = """
    <html>
    <body>
        <h1>CSV file for the Venue: {{ venue_name }}</h1>
        <p>Location: {{ venue_place }}, {{ venue_city }}</p>
        <p>Capacity: {{ capacity }}</p>
        <p>Number of shows: {{ show_num }}</p>
        <p>Number of bookings: {{ bookings }}</p>
    </body>
    </html>
    """

    # Create a Jinja2 Template object from the HTML template string
    msg_template = Template(html_template)

    # Create the csv file
    with open(file=filepath, mode='w') as file:
        csv_obj = csv.writer(file, delimiter=',')

        csv_obj.writerow(['Venue id', 'Name', 'Location', "Capacity", "Total Shows", "Total Bookings"])
        csv_obj.writerow([venue_id, venue_data.name, venue_data.place + ', ' + venue_data.city, venue_data.capacity, shows, bookings])

    subject = 'CSV file for ' + venue_data.name
    body = msg_template.render(venue_name=venue_data.name, venue_place=venue_data.place, venue_city = venue_data.city, capacity = venue_data.capacity, show_num = shows, bookings=bookings)
    recipients = [user.email]
    reci1 = ','.join(recipients)

    print(reci1)
    send_email(to=recipients, subject=subject, msg = body, attachment=filepath)

    return 'success'