import os
import sqlite3
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, g
from forms import ContactForm, BusBookingForm, ApartmentBookingForm, TourBookingForm


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '\xeaF\x0b\xce\xee#9Z\xae\x0e\xbd\x98\x02T\xf7bU\xc7\xfe\xd6cg\x93\xda')
IS_VERCEL = os.environ.get('VERCEL', False)
DATABASE = os.path.join('/tmp' if IS_VERCEL else os.path.dirname(os.path.abspath(__file__)), 'bookings.db')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute('''
        CREATE TABLE IF NOT EXISTS bus_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT NOT NULL,
            bus_type TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS apartment_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            apartment_type TEXT NOT NULL,
            checkin_date TEXT NOT NULL,
            checkout_date TEXT NOT NULL,
            guests INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS tour_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            depart_date TEXT NOT NULL,
            travellers INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    db.commit()
    db.close()


@app.before_request
def ensure_db():
    if not os.path.exists(DATABASE):
        init_db()


# --- Pages ---

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/buses")
def buses():
    return render_template('buses.html', bus_form=BusBookingForm())


@app.route("/apartments")
def apartments():
    return render_template('apartments.html', apt_form=ApartmentBookingForm())


@app.route("/tours")
def tours():
    return render_template('tours.html', tour_form=TourBookingForm())


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    form_success = False

    if request.method == "POST" and form.validate_on_submit():
        db = get_db()
        db.execute(
            'INSERT INTO contact_messages (name, email, subject, message, created_at) VALUES (?, ?, ?, ?, ?)',
            (form.name.data, form.email.data, form.subject.data, form.message.data, datetime.now().isoformat())
        )
        db.commit()
        form_success = True
        form.name.data, form.email.data, form.subject.data, form.message.data = "", "", "", ""

    return render_template('contact.html', form=form, form_success=form_success)


# --- Booking Handlers ---

@app.route("/book-bus", methods=["POST"])
def book_bus():
    form = BusBookingForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute(
            'INSERT INTO bus_bookings (route, bus_type, travel_date, full_name, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (form.route.data, form.bus_type.data, form.travel_date.data, form.full_name.data, form.phone.data, datetime.now().isoformat())
        )
        db.commit()
        flash('Your quote request has been submitted! We will contact you with pricing shortly.', 'success')
    else:
        flash('Please fill in all fields correctly.', 'error')
    return redirect(url_for('buses'))


@app.route("/book-apartment", methods=["POST"])
def book_apartment():
    form = ApartmentBookingForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute(
            'INSERT INTO apartment_bookings (location, apartment_type, checkin_date, checkout_date, guests, full_name, phone, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (form.location.data, form.apartment_type.data, form.checkin_date.data, form.checkout_date.data, form.guests.data, form.full_name.data, form.phone.data, datetime.now().isoformat())
        )
        db.commit()
        flash('Your apartment booking has been submitted successfully! We will contact you shortly.', 'success')
    else:
        flash('Please fill in all fields correctly.', 'error')
    return redirect(url_for('apartments'))


@app.route("/book-tour", methods=["POST"])
def book_tour():
    form = TourBookingForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute(
            'INSERT INTO tour_bookings (destination, depart_date, travellers, full_name, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (form.destination.data, form.depart_date.data, form.travellers.data, form.full_name.data, form.phone.data, datetime.now().isoformat())
        )
        db.commit()
        flash('Your tour booking has been submitted successfully! We will contact you shortly.', 'success')
    else:
        flash('Please fill in all fields correctly.', 'error')
    return redirect(url_for('tours'))


if __name__ == '__main__':
    app.run(debug=True)
