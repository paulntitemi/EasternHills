from flask import Flask, request, render_template
from env.forms import ContactForm

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xeaF\x0b\xce\xee#9Z\xae\x0e\xbd\x98\x02T\xf7bU\xc7\xfe\xd6cg\x93\xda'


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/blog")
def blog():
    return render_template('blog.html')


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if request == "POST":
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data
        print(name, email, message)

        form.name.data, form.email.data, form.subject.data, form.message.data = "", "", "", ""

        return render_template('contact.html', form=form, success=True)
    return render_template('contact.html', form=form)


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
