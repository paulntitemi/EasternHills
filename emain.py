import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, g, session, jsonify
from forms import (ContactForm, BusSearchForm, BusCheckoutForm, ApartmentBookingForm, TourBookingForm,
                   get_bus_price, get_apartment_price, TOUR_PRICES, BUS_PRICE_MAP,
                   BUS_MODELS, BUS_EXTRAS, get_bus_model, get_bus_extra, calculate_bus_total)


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
    return render_template('buses.html', search_form=BusSearchForm())


@app.route("/buses/search", methods=["POST"])
def buses_search():
    form = BusSearchForm()
    destinations = request.form.getlist('destinations[]')

    if not form.validate_on_submit() or not destinations:
        if not destinations:
            flash('Please select at least one destination.', 'error')
        else:
            flash('Please fill in all required fields.', 'error')
        return redirect(url_for('buses'))

    session['bus_search'] = {
        'trip_type': form.trip_type.data,
        'pickup_location': form.pickup_location.data,
        'destinations': destinations,
        'travel_date': form.travel_date.data,
        'return_date': form.return_date.data or '',
        'days': form.days.data,
    }
    return redirect(url_for('buses_results'))


@app.route("/buses/results")
def buses_results():
    search = session.get('bus_search')
    if not search:
        flash('Please start a new search.', 'error')
        return redirect(url_for('buses'))

    # Calculate price for each model
    results = []
    for model in BUS_MODELS:
        price = calculate_bus_total(
            model['id'],
            search['destinations'],
            search['trip_type'],
            search['days']
        )
        results.append({**model, 'price': price})

    return render_template('buses_results.html', search=search, results=results)


@app.route("/buses/select/<model_id>")
def buses_select(model_id):
    search = session.get('bus_search')
    if not search:
        return redirect(url_for('buses'))

    model = get_bus_model(model_id)
    if not model:
        flash('Invalid bus selection.', 'error')
        return redirect(url_for('buses_results'))

    session['bus_selection'] = model_id
    return redirect(url_for('buses_checkout'))


@app.route("/buses/checkout", methods=["GET", "POST"])
def buses_checkout():
    search = session.get('bus_search')
    model_id = session.get('bus_selection')
    if not search or not model_id:
        return redirect(url_for('buses'))

    model = get_bus_model(model_id)
    if not model:
        return redirect(url_for('buses_results'))

    form = BusCheckoutForm()
    selected_extras = request.form.getlist('extras[]') if request.method == 'POST' else []

    base_price = calculate_bus_total(model_id, search['destinations'], search['trip_type'], search['days'])
    extras_total = sum(get_bus_extra(e)['price'] for e in selected_extras if get_bus_extra(e))
    total = base_price + extras_total

    if request.method == "POST" and form.validate_on_submit():
        trip_label = 'Round Trip' if search['trip_type'] == 'round_trip' else 'One Way'
        dest_str = ', '.join(search['destinations'])
        days = search['days']
        lines = [
            model['name'],
            f"{search['pickup_location']} — {dest_str}",
            trip_label,
            f"{days} day{'s' if days > 1 else ''}",
        ]
        if selected_extras:
            lines.append('Extras:')
            for eid in selected_extras:
                extra = get_bus_extra(eid)
                if extra:
                    lines.append(extra['name'])
        details = '\n'.join(lines)

        travel_date_str = search['travel_date']
        if search.get('return_date'):
            travel_date_str += f" to {search['return_date']}"

        reservation_code = generate_reservation_code()
        db = get_db()
        db.execute(
            'INSERT INTO bookings (reservation_code, booking_type, details, travel_date, amount, full_name, email, phone, payment_status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (reservation_code, 'bus', details, travel_date_str, total, form.full_name.data, form.email.data, form.phone.data, 'paid', datetime.now().isoformat())
        )
        db.commit()

        # Clear session
        session.pop('bus_search', None)
        session.pop('bus_selection', None)

        return redirect(url_for('confirmation', reservation_code=reservation_code))

    return render_template('buses_checkout.html',
        search=search,
        model=model,
        base_price=base_price,
        extras=BUS_EXTRAS,
        selected_extras=selected_extras,
        extras_total=extras_total,
        total=total,
        form=form,
    )


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


# --- Apartment & Tour Booking (legacy single-step flow) ---

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
