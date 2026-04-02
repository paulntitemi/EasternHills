from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange
import email_validator


BUS_ROUTES = [
    ('', 'Select Route'),
    ('Accra to Kumasi', 'Accra to Kumasi'),
    ('Kumasi to Accra', 'Kumasi to Accra'),
    ('Accra to Cape Coast', 'Accra to Cape Coast'),
    ('Cape Coast to Accra', 'Cape Coast to Accra'),
    ('Accra to Tamale', 'Accra to Tamale'),
    ('Tamale to Accra', 'Tamale to Accra'),
    ('Accra to Ho', 'Accra to Ho'),
    ('Ho to Accra', 'Ho to Accra'),
    ('Accra to Takoradi', 'Accra to Takoradi'),
    ('Takoradi to Accra', 'Takoradi to Accra'),
    ('Kumasi to Tamale', 'Kumasi to Tamale'),
    ('Tamale to Kumasi', 'Tamale to Kumasi'),
    ('Accra to Koforidua', 'Accra to Koforidua'),
    ('Koforidua to Accra', 'Koforidua to Accra'),
    ('Accra to Sunyani', 'Accra to Sunyani'),
    ('Sunyani to Accra', 'Sunyani to Accra'),
]

BUS_TYPES = [
    ('', 'Select Bus Size'),
    ('Sprinter (15-seater)', 'Sprinter (15-seater)'),
    ('Coaster (30-seater)', 'Coaster (30-seater)'),
    ('Full Coach (50-seater)', 'Full Coach (50-seater)'),
]

APARTMENT_LOCATIONS = [
    ('', 'Select Location'),
    ('Accra - East Legon', 'Accra - East Legon'),
    ('Accra - Airport Area', 'Accra - Airport Area'),
    ('Accra - Osu', 'Accra - Osu'),
    ('Accra - Cantonments', 'Accra - Cantonments'),
    ('Accra - Labone', 'Accra - Labone'),
    ('Kumasi', 'Kumasi'),
    ('Cape Coast', 'Cape Coast'),
    ('Takoradi', 'Takoradi'),
    ('Tamale', 'Tamale'),
    ('Ho', 'Ho'),
    ('Koforidua', 'Koforidua'),
]

APARTMENT_TYPES = [
    ('', 'Select Type'),
    ('Studio', 'Studio'),
    ('1-Bedroom', '1-Bedroom'),
    ('2-Bedroom', '2-Bedroom'),
    ('3-Bedroom', '3-Bedroom'),
]

TOUR_DESTINATIONS = [
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


# --- Pricing (placeholder rates — adjust as needed) ---

BUS_PRICES = {
    'Sprinter (15-seater)': {
        'short': 800,   # Accra-Cape Coast, Accra-Ho, Accra-Koforidua
        'medium': 1200,  # Accra-Kumasi, Accra-Takoradi, Accra-Sunyani
        'long': 2500,    # Accra-Tamale, Kumasi-Tamale
    },
    'Coaster (30-seater)': {
        'short': 1500,
        'medium': 2200,
        'long': 4000,
    },
    'Full Coach (50-seater)': {
        'short': 2500,
        'medium': 3500,
        'long': 6000,
    },
}

ROUTE_DISTANCE = {
    'Accra to Kumasi': 'medium',
    'Kumasi to Accra': 'medium',
    'Accra to Cape Coast': 'short',
    'Cape Coast to Accra': 'short',
    'Accra to Tamale': 'long',
    'Tamale to Accra': 'long',
    'Accra to Ho': 'short',
    'Ho to Accra': 'short',
    'Accra to Takoradi': 'medium',
    'Takoradi to Accra': 'medium',
    'Kumasi to Tamale': 'long',
    'Tamale to Kumasi': 'long',
    'Accra to Koforidua': 'short',
    'Koforidua to Accra': 'short',
    'Accra to Sunyani': 'medium',
    'Sunyani to Accra': 'medium',
}

APARTMENT_PRICES = {
    'Studio': 200,
    '1-Bedroom': 280,
    '2-Bedroom': 350,
    '3-Bedroom': 450,
}

TOUR_PRICES = {
    'default': 500,
}


def get_bus_price(route, bus_type):
    distance = ROUTE_DISTANCE.get(route, 'medium')
    return BUS_PRICES.get(bus_type, {}).get(distance, 1500)


def get_apartment_price(apartment_type):
    return APARTMENT_PRICES.get(apartment_type, 250)


# --- Forms ---

class ContactForm(FlaskForm):
    name = StringField("NAME", validators=[DataRequired('A full name is required'), Length(min=5, max=30)])
    email = StringField("EMAIL", validators=[DataRequired('A correct email is required'), Email()])
    subject = StringField("SUBJECT", validators=[DataRequired('A subject is required')])
    message = TextAreaField("MESSAGE", validators=[DataRequired('A message is required'), Length(min=5, max=500)])
    submit = SubmitField("SEND")


class BusBookingForm(FlaskForm):
    route = SelectField('Route', choices=BUS_ROUTES, validators=[DataRequired('Please select a route')])
    bus_type = SelectField('Bus Size', choices=BUS_TYPES, validators=[DataRequired('Please select a bus size')])
    travel_date = StringField('Travel Date', validators=[DataRequired('Please select a travel date')])
    full_name = StringField('Full Name', validators=[DataRequired('Please enter your full name'), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired('Please enter your email'), Email()])
    phone = StringField('Phone', validators=[DataRequired('Please enter your phone number'), Length(min=7, max=20)])
    submit = SubmitField('Proceed to Payment')


class ApartmentBookingForm(FlaskForm):
    location = SelectField('Location', choices=APARTMENT_LOCATIONS, validators=[DataRequired('Please select a location')])
    apartment_type = SelectField('Type', choices=APARTMENT_TYPES, validators=[DataRequired('Please select apartment type')])
    checkin_date = StringField('Check-in', validators=[DataRequired('Please select check-in date')])
    checkout_date = StringField('Check-out', validators=[DataRequired('Please select check-out date')])
    guests = IntegerField('Guests', validators=[DataRequired('Please enter number of guests'), NumberRange(min=1, max=10)])
    full_name = StringField('Full Name', validators=[DataRequired('Please enter your full name'), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired('Please enter your email'), Email()])
    phone = StringField('Phone', validators=[DataRequired('Please enter your phone number'), Length(min=7, max=20)])
    submit = SubmitField('Proceed to Payment')


class TourBookingForm(FlaskForm):
    destination = SelectField('Destination', choices=TOUR_DESTINATIONS, validators=[DataRequired('Please select a destination')])
    depart_date = StringField('Depart Date', validators=[DataRequired('Please select a departure date')])
    travellers = IntegerField('Travellers', validators=[DataRequired('Please enter number of travellers'), NumberRange(min=1, max=50)])
    full_name = StringField('Full Name', validators=[DataRequired('Please enter your full name'), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired('Please enter your email'), Email()])
    phone = StringField('Phone', validators=[DataRequired('Please enter your phone number'), Length(min=7, max=20)])
    submit = SubmitField('Proceed to Payment')
