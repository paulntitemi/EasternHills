from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange
import email_validator


DESTINATIONS = [
    ('', 'Select Destination'),
    ('Aburi Botanical Gardens', 'Aburi Botanical Gardens'),
    ('Accra Zoo', 'Accra Zoo'),
    ('Ada Foah Beach', 'Ada Foah Beach'),
    ('Ankasa Forest', 'Ankasa Forest'),
    ('Bobiri Forest and Butterfly Sanctuary', 'Bobiri Forest and Butterfly Sanctuary'),
    ('Boabeng Fiema Monkey Sanctuary', 'Boabeng Fiema Monkey Sanctuary'),
    ('Bunsu Arboretum', 'Bunsu Arboretum'),
    ('Buoyam Caves', 'Buoyam Caves'),
    ('Cape Coast Castle', 'Cape Coast Castle'),
    ('Cape Three Point', 'Cape Three Point'),
    ('Dubois Memorial Centre', 'Dubois Memorial Centre'),
    ('Elmina Castle', 'Elmina Castle'),
    ('Gemi Amedzofe (Mountain)', 'Gemi Amedzofe (Mountain)'),
    ('Ghana Museum', 'Ghana Museum'),
    ('Kakum National Park', 'Kakum National Park'),
    ('Kintampo Waterfalls', 'Kintampo Waterfalls'),
    ('Kumasi Armed Forces Military Museum', 'Kumasi Armed Forces Military Museum'),
    ('Kumasi Zoo', 'Kumasi Zoo'),
    ('Kyabobo National Park', 'Kyabobo National Park'),
    ('Manhyia Palace', 'Manhyia Palace'),
    ('Mole National Park', 'Mole National Park'),
    ('Mognori Eco Village', 'Mognori Eco Village'),
    ('Mountain Afadjato (Tagbo Waterfall)', 'Mountain Afadjato (Tagbo Waterfall)'),
    ('Nkrumah Memorial Park', 'Nkrumah Memorial Park'),
    ('Nzulezu Stilt Village', 'Nzulezu Stilt Village'),
    ('Obuasi Mine', 'Obuasi Mine'),
    ('Okomfo Anokye Sword', 'Okomfo Anokye Sword'),
    ('Paga Chief Pond', 'Paga Chief Pond'),
    ('Paga Zenga Crocodile Pond', 'Paga Zenga Crocodile Pond'),
    ('Pikworo Nania Slave Camp', 'Pikworo Nania Slave Camp'),
    ('Prempeh Jubilee', 'Prempeh Jubilee'),
    ('Shai Hills', 'Shai Hills'),
    ('Sirigu Women Organisation for Pottery Art', 'Sirigu Women Organisation for Pottery Art'),
    ('Tagbo Waterfall / Mountain Afadjato', 'Tagbo Waterfall / Mountain Afadjato'),
    ('Tafi Atome Monkey Sanctuary', 'Tafi Atome Monkey Sanctuary'),
    ('Tango Hills / Tingzag Shrine', 'Tango Hills / Tingzag Shrine'),
    ('Tano Boase Sacred Grove', 'Tano Boase Sacred Grove'),
    ('Wassa Domama Rock Shrine', 'Wassa Domama Rock Shrine'),
    ('Wechiau Hippo Sanctuary', 'Wechiau Hippo Sanctuary'),
    ('Wli Waterfalls', 'Wli Waterfalls'),
    ('Xavi Bird Sanctuary', 'Xavi Bird Sanctuary'),
]


class ContactForm(FlaskForm):

    name = StringField("NAME", validators=[DataRequired('A full name is required'), Length(min=5, max=30)])
    email = StringField("EMAIL", validators=[DataRequired('A correct email is required'), Email()])
    subject = StringField("SUBJECT", validators=[DataRequired('A subject is required')])
    message = TextAreaField("MESSAGE", validators=[DataRequired('A message is required'), Length(min=5, max=500)])
    submit = SubmitField("SEND")


class BookingForm(FlaskForm):
    destination = SelectField(
        'Destination',
        choices=DESTINATIONS,
        validators=[DataRequired('Please select a destination')]
    )

    depart_date = StringField(
        'Depart Date',
        validators=[DataRequired('Please select a departure date')]
    )

    travellers = IntegerField(
        'Number of Travellers',
        validators=[DataRequired('Please enter number of travellers'), NumberRange(min=1, max=50, message='Must be between 1 and 50')]
    )

    full_name = StringField(
        'Full Name',
        validators=[DataRequired('Please enter your full name'), Length(min=2, max=100)]
    )

    phone = StringField(
        'Phone / WhatsApp',
        validators=[DataRequired('Please enter your phone number'), Length(min=7, max=20)]
    )

    submit = SubmitField('Book Now')
