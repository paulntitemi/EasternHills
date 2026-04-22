import os
import sqlite3
import uuid
from functools import wraps
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, g, session, jsonify
from flask_cors import CORS
from forms import (ContactForm, BusSearchForm, BusCheckoutForm, ApartmentBookingForm, TourBookingForm,
                   get_bus_price, get_apartment_price, TOUR_PRICES, BUS_PRICE_MAP,
                   BUS_MODELS, BUS_EXTRAS, get_bus_model, get_bus_extra, calculate_bus_total)


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '\xeaF\x0b\xce\xee#9Z\xae\x0e\xbd\x98\x02T\xf7bU\xc7\xfe\xd6cg\x93\xda')
IS_VERCEL = os.environ.get('VERCEL', False)
DATABASE = os.path.join('/tmp' if IS_VERCEL else os.path.dirname(os.path.abspath(__file__)), 'bookings.db')

ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'dev-token-change-me')

# Allow the admin dashboard (React dev + any deployed admin origin) to call /api/*
CORS(app, resources={r"/api/*": {"origins": os.environ.get('ADMIN_ORIGINS', 'http://localhost:5173').split(',')}})


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-Admin-Token')
        if not token or token != ADMIN_TOKEN:
            return jsonify({'error': 'unauthorized'}), 401
        return fn(*args, **kwargs)
    return wrapper


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
    # Safe column migrations — add admin-side fields if missing
    existing_cols = {row[1] for row in db.execute("PRAGMA table_info(bookings)")}
    for col, ddl in [
        ('driver_id', 'ALTER TABLE bookings ADD COLUMN driver_id TEXT'),
        ('vehicle_id', 'ALTER TABLE bookings ADD COLUMN vehicle_id TEXT'),
        ('admin_status', 'ALTER TABLE bookings ADD COLUMN admin_status TEXT'),
        ('admin_events', "ALTER TABLE bookings ADD COLUMN admin_events TEXT DEFAULT '[]'"),
    ]:
        if col not in existing_cols:
            db.execute(ddl)

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


_db_initialised = False

@app.before_request
def ensure_db():
    global _db_initialised
    if not _db_initialised or not os.path.exists(DATABASE):
        init_db()
        _db_initialised = True


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


# --- Admin API (consumed by React dashboard) ---

def _parse_pickup_dropoff(details):
    """Best-effort extract pickup/destination from the multi-line details string."""
    if not details:
        return ('', '')
    lines = [l.strip() for l in details.split('\n') if l.strip()]
    # Line 0 = vehicle/model, line 1 is usually "Pickup — destinations"
    for line in lines[1:3]:
        if '—' in line:
            left, right = line.split('—', 1)
            return (left.strip(), right.strip())
    return (lines[1] if len(lines) > 1 else '', '')


def _row_get(row, key, default=None):
    """Safe column access — handles rows from before a column was added."""
    try:
        value = row[key]
        return value if value is not None else default
    except (IndexError, KeyError):
        return default


def _parse_travel_dates(s):
    """Website stores travel_date as '05/20/2026' or '04/20/2026 to 04/22/2026'.
    Return (pickup_iso, dropoff_iso). Falls back to the raw string if parsing fails.
    """
    if not s:
        return (None, None)
    parts = [p.strip() for p in s.split(' to ')]
    pickup_raw = parts[0]
    dropoff_raw = parts[1] if len(parts) > 1 else parts[0]

    def to_iso(raw):
        for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y'):
            try:
                return datetime.strptime(raw, fmt).isoformat()
            except ValueError:
                continue
        return raw  # fall back to the raw string

    return (to_iso(pickup_raw), to_iso(dropoff_raw))


def booking_to_admin_json(row):
    """Map a Flask booking row into the admin dashboard's Reservation shape."""
    import json
    pickup, dropoff = _parse_pickup_dropoff(row['details'])
    pickup_iso, dropoff_iso = _parse_travel_dates(row['travel_date'])
    payment = row['payment_status']

    # Admin-overridden status wins over derived status
    admin_status = _row_get(row, 'admin_status')
    if admin_status:
        status = admin_status
    elif payment == 'paid':
        status = 'Confirmed'
    elif payment == 'pending':
        status = 'Pending'
    else:
        status = payment.title()

    history = [{'action': 'Created', 'at': row['created_at']}]
    if payment == 'paid':
        history.append({'action': 'Payment Received', 'at': row['created_at']})

    # Append any admin-made changes
    try:
        admin_events = json.loads(_row_get(row, 'admin_events', '[]') or '[]')
        history.extend(admin_events)
    except (ValueError, TypeError):
        pass

    return {
        'id': row['reservation_code'],
        'source': row['booking_type'],  # 'bus' | 'apartment' | 'tour'
        'customerId': None,
        'customerName': row['full_name'],
        'customerPhone': row['phone'],
        'customerEmail': row['email'],
        'pickupLocation': pickup or row['booking_type'].title(),
        'dropoffLocation': dropoff or '—',
        'pickupDate': pickup_iso or row['travel_date'],
        'dropoffDate': dropoff_iso or row['travel_date'],
        'vehicleId': _row_get(row, 'vehicle_id'),
        'driverId': _row_get(row, 'driver_id'),
        'status': status,
        'baseRate': row['amount'],
        'extras': 0,
        'insurance': 0,
        'total': row['amount'],
        'notes': row['details'] or '',
        'createdAt': row['created_at'],
        'history': history,
    }


@app.route("/api/admin/bookings", methods=["GET"])
@require_admin
def api_list_bookings():
    db = get_db()
    rows = db.execute('SELECT * FROM bookings ORDER BY created_at DESC').fetchall()
    return jsonify([booking_to_admin_json(r) for r in rows])


@app.route("/api/admin/bookings/<reservation_code>", methods=["GET"])
@require_admin
def api_get_booking(reservation_code):
    db = get_db()
    row = db.execute('SELECT * FROM bookings WHERE reservation_code = ?', (reservation_code,)).fetchone()
    if not row:
        return jsonify({'error': 'not found'}), 404
    return jsonify(booking_to_admin_json(row))


@app.route("/api/admin/bookings/<reservation_code>", methods=["PATCH"])
@require_admin
def api_patch_booking(reservation_code):
    """Partial update from the admin dashboard. Supports status, driverId, vehicleId."""
    import json
    db = get_db()
    row = db.execute('SELECT * FROM bookings WHERE reservation_code = ?', (reservation_code,)).fetchone()
    if not row:
        return jsonify({'error': 'not found'}), 404

    data = request.get_json(force=True, silent=True) or {}
    events = []
    try:
        events = json.loads(_row_get(row, 'admin_events', '[]') or '[]')
    except (ValueError, TypeError):
        events = []

    now = datetime.now().isoformat()
    sets = []
    params = []
    actor = request.headers.get('X-Admin-Actor', 'Admin')

    if 'status' in data:
        sets.append('admin_status = ?')
        params.append(data['status'])
        events.append({'action': f"Status → {data['status']}", 'at': now, 'actor': actor})

    if 'driverId' in data:
        sets.append('driver_id = ?')
        params.append(data['driverId'])
        if data['driverId']:
            events.append({'action': f"Driver assigned ({data['driverId']})", 'at': now, 'actor': actor})
        else:
            events.append({'action': 'Driver unassigned', 'at': now, 'actor': actor})

    if 'vehicleId' in data:
        sets.append('vehicle_id = ?')
        params.append(data['vehicleId'])
        if data['vehicleId']:
            events.append({'action': f"Vehicle assigned ({data['vehicleId']})", 'at': now, 'actor': actor})
        else:
            events.append({'action': 'Vehicle unassigned', 'at': now, 'actor': actor})

    if not sets:
        return jsonify({'error': 'no changes'}), 400

    sets.append('admin_events = ?')
    params.append(json.dumps(events))
    params.append(reservation_code)

    db.execute(f"UPDATE bookings SET {', '.join(sets)} WHERE reservation_code = ?", params)
    db.commit()

    updated = db.execute('SELECT * FROM bookings WHERE reservation_code = ?', (reservation_code,)).fetchone()
    return jsonify(booking_to_admin_json(updated))


@app.route("/api/admin/stats", methods=["GET"])
@require_admin
def api_stats():
    """Quick summary for the admin dashboard to verify the pipe is working."""
    db = get_db()
    total = db.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
    paid = db.execute("SELECT COUNT(*) FROM bookings WHERE payment_status = 'paid'").fetchone()[0]
    revenue = db.execute("SELECT COALESCE(SUM(amount), 0) FROM bookings WHERE payment_status = 'paid'").fetchone()[0]
    return jsonify({
        'totalBookings': total,
        'paidBookings': paid,
        'revenue': revenue,
    })


if __name__ == '__main__':
    app.run(debug=True)
