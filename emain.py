from flask import Flask, request, render_template
from env.forms import ContactForm, BookingForm



app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = '\xeaF\x0b\xce\xee#9Z\xae\x0e\xbd\x98\x02T\xf7bU\xc7\xfe\xd6cg\x93\xda'



@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/blog")
def blog():
    return render_template('blog.html')


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    booking_form = BookingForm()
    form_success = False
    booking_form_success = False

    if request.method == "POST":
        if 'submit' in request.form and form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            subject = form.subject.data
            message = form.message.data
            print("Contact Form:", name, email, subject, message)
            form_success = True
            # Additional logic for Contact Form (e.g., sending email)

            form.name.data, form.email.data, form.subject.data, form.message.data = "", "", "", ""

        if 'booking_submit' in request.form and booking_form.validate():
            # Process Booking Form
            destination = booking_form.destination.data
            depart_date = booking_form.depart_date.data
            return_date = booking_form.return_date.data
            duration = booking_form.duration.data
            print("Booking Form:", destination, depart_date, return_date, duration)
            booking_form_success = True
            # Additional logic for Booking Form

            booking_form.destination.data, booking_form.depart_date.data, booking_form.return_date.data, booking_form.duration.data = "", "", "", ""

    return render_template('contact.html', form=form, booking_form=booking_form, form_success=form_success, booking_form_success=booking_form_success)



@app.route("/destination")
def destination():
    return render_template('destination.html')


@app.route("/guide")
def guide():
    return render_template('guide.html')


@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/package")
def package():
    return render_template('package.html')


@app.route("/service")
def service():
    return render_template('service.html')


@app.route("/single")
def single():
    return render_template('single.html')


@app.route("/testimonial")
def testimonial():
    return render_template('testimonial.html')


if __name__ == '__main__':
    app.run(debug=True)