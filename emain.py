import os
import sqlite3
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, g
from forms import ContactForm, BookingForm



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
        CREATE TABLE IF NOT EXISTS bookings (
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


@app.route("/book", methods=["POST"])
def book():
    form = BookingForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute(
            'INSERT INTO bookings (destination, depart_date, travellers, full_name, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (form.destination.data, form.depart_date.data, form.travellers.data, form.full_name.data, form.phone.data, datetime.now().isoformat())
        )
        db.commit()
        flash('Your booking inquiry has been submitted successfully! We will contact you shortly.', 'booking_success')
    else:
        flash('Please fill in all fields correctly.', 'booking_error')
    return redirect(request.referrer or url_for('home'))


@app.route("/about")
def about():
    return render_template('about.html', booking_form=BookingForm())


@app.route("/blog")
def blog():
    return render_template('blog.html', booking_form=BookingForm())


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    booking_form = BookingForm()
    form_success = False

    if request.method == "POST":
        if 'submit' in request.form and form.validate_on_submit():
            db = get_db()
            db.execute(
                'INSERT INTO contact_messages (name, email, subject, message, created_at) VALUES (?, ?, ?, ?, ?)',
                (form.name.data, form.email.data, form.subject.data, form.message.data, datetime.now().isoformat())
            )
            db.commit()
            form_success = True
            form.name.data, form.email.data, form.subject.data, form.message.data = "", "", "", ""

    return render_template('contact.html', form=form, booking_form=booking_form, form_success=form_success)


@app.route("/destination")
def destination():
    return render_template('destination.html', booking_form=BookingForm())


@app.route("/guide")
def guide():
    return render_template('guide.html', booking_form=BookingForm())


@app.route("/index")
def index():
    return render_template('index.html', booking_form=BookingForm())


@app.route("/")
def home():
    return render_template('index.html', booking_form=BookingForm())


@app.route("/package")
def package():
    return render_template('package.html', booking_form=BookingForm())


@app.route("/service")
def service():
    return render_template('service.html', booking_form=BookingForm())


@app.route("/single")
def single():
    return render_template('single.html', booking_form=BookingForm())


@app.route("/testimonial")
def testimonial():
    return render_template('testimonial.html', booking_form=BookingForm())


if __name__ == '__main__':
    app.run(debug=True)
