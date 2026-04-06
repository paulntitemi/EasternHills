import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, g, session, jsonify
from forms import (ContactForm, BusBookingForm, ApartmentBookingForm, TourBookingForm,
                   get_bus_price, get_apartment_price, TOUR_PRICES, BUS_PRICE_MAP)


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


def generate_reservation_code():
    return 'EH-' + uuid.uuid4().hex[:8].upper()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reservation_code TEXT UNIQUE NOT NULL,
            booking_type TEXT NOT NULL,
            details TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            amount INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            payment_status TEXT NOT NULL DEFAULT 'pending',
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


# --- API: Price lookup ---

@app.route("/api/bus-price")
def api_bus_price():
    bus_type = request.args.get('bus_type', '')
    trip_type = request.args.get('trip_type', 'one_way')
    days = int(request.args.get('days', 1) or 1)
    destinations = request.args.getlist('destinations[]')

    if not bus_type or not destinations:
        return jsonify({'price': None, 'breakdown': []})

    breakdown = []
    total = 0
    for dest in destinations:
        base = BUS_PRICE_MAP.get(dest, {}).get(bus_type, 0)
        if base:
            breakdown.append({'destination': dest, 'base_price': base})
            total += base

    if trip_type == 'round_trip':
        total = total * 2
    total = total * max(days, 1)

    return jsonify({
        'price': total,
        'breakdown': breakdown,
        'trip_type': trip_type,
        'days': days,
    })


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


# --- Booking Flow: Step 1 - Validate & show payment page ---

@app.route("/book-bus", methods=["POST"])
def book_bus():
    form = BusBookingForm()
    if form.validate_on_submit():
        destinations = request.form.getlist('destinations[]')
        if not destinations:
            flash('Please select at least one destination.', 'error')
            return redirect(url_for('buses'))

        trip_type = form.trip_type.data
        days = form.days.data or 1
        total = 0
        for dest in destinations:
            total += BUS_PRICE_MAP.get(dest, {}).get(form.bus_type.data, 0)
        if trip_type == 'round_trip':
            total *= 2
        total *= days

        pickup = request.form.get('pickup_point', '')
        trip_label = 'Round Trip' if trip_type == 'round_trip' else 'One Way'
        dest_str = ' + '.join(destinations)
        pickup_str = f"From {pickup} to " if pickup else ''
        details = f"{form.bus_type.data} — {pickup_str}{dest_str} ({trip_label}, {days} day{'s' if days > 1 else ''})"

        travel_date_str = form.travel_date.data
        if form.return_date.data:
            travel_date_str += f" to {form.return_date.data}"

        reservation_code = generate_reservation_code()
        db = get_db()
        db.execute(
            'INSERT INTO bookings (reservation_code, booking_type, details, travel_date, amount, full_name, email, phone, payment_status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (reservation_code, 'bus', details, travel_date_str, total, form.full_name.data, form.email.data, form.phone.data, 'pending', datetime.now().isoformat())
        )
        db.commit()

        return render_template('payment.html',
            reservation_code=reservation_code,
            booking_type='Bus Rental',
            details=details,
            travel_date=travel_date_str,
            amount=total,
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
        )
    flash('Please fill in all fields correctly.', 'error')
    return redirect(url_for('buses'))


@app.route("/book-apartment", methods=["POST"])
def book_apartment():
    form = ApartmentBookingForm()
    if form.validate_on_submit():
        price_per_night = get_apartment_price(form.apartment_type.data)
        details = f"{form.apartment_type.data} — {form.location.data}"
        reservation_code = generate_reservation_code()

        db = get_db()
        db.execute(
            'INSERT INTO bookings (reservation_code, booking_type, details, travel_date, amount, full_name, email, phone, payment_status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (reservation_code, 'apartment', details, f"{form.checkin_date.data} to {form.checkout_date.data}",
             price_per_night, form.full_name.data, form.email.data, form.phone.data, 'pending', datetime.now().isoformat())
        )
        db.commit()

        return render_template('payment.html',
            reservation_code=reservation_code,
            booking_type='Apartment Stay',
            details=details,
            travel_date=f"{form.checkin_date.data} — {form.checkout_date.data}",
            amount=price_per_night,
            amount_note='per night',
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
        )
    flash('Please fill in all fields correctly.', 'error')
    return redirect(url_for('apartments'))


@app.route("/book-tour", methods=["POST"])
def book_tour():
    form = TourBookingForm()
    if form.validate_on_submit():
        price = TOUR_PRICES.get('default', 500)
        details = f"{form.destination.data} — {form.travellers.data} traveller(s)"
        reservation_code = generate_reservation_code()

        db = get_db()
        db.execute(
            'INSERT INTO bookings (reservation_code, booking_type, details, travel_date, amount, full_name, email, phone, payment_status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (reservation_code, 'tour', details, form.depart_date.data, price, form.full_name.data, form.email.data, form.phone.data, 'pending', datetime.now().isoformat())
        )
        db.commit()

        return render_template('payment.html',
            reservation_code=reservation_code,
            booking_type='Tour Package',
            details=details,
            travel_date=form.depart_date.data,
            amount=price,
            amount_note='per person',
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
        )
    flash('Please fill in all fields correctly.', 'error')
    return redirect(url_for('tours'))


# --- Booking Flow: Step 2 - Process payment (placeholder) ---

@app.route("/process-payment/<reservation_code>", methods=["POST"])
def process_payment(reservation_code):
    payment_method = request.form.get('payment_method', 'card')

    db = get_db()
    booking = db.execute('SELECT * FROM bookings WHERE reservation_code = ?', (reservation_code,)).fetchone()

    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('home'))

    # --- PLACEHOLDER: This is where Paystack/Flutterwave integration goes ---
    # For now, we simulate a successful payment
    db.execute('UPDATE bookings SET payment_status = ? WHERE reservation_code = ?', ('paid', reservation_code))
    db.commit()

    return redirect(url_for('confirmation', reservation_code=reservation_code))


# --- Booking Flow: Step 3 - Confirmation page ---

@app.route("/confirmation/<reservation_code>")
def confirmation(reservation_code):
    db = get_db()
    booking = db.execute('SELECT * FROM bookings WHERE reservation_code = ?', (reservation_code,)).fetchone()

    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('home'))

    return render_template('confirmation.html', booking=booking)


if __name__ == '__main__':
    app.run(debug=True)
