from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional
import email_validator


# --- Bus Destinations & Pricing (from rate card) ---
# Each destination: (value, label, coaster_price, hiace_price)

BUS_DESTINATIONS_DATA = [
    # Greater Accra
    ('Greater Accra', 'Greater Accra', 1400, 1400),
    ('Ada', 'Ada', 1450, 1450),
    # Central Region
    ('Winneba / Swedru', 'Winneba / Swedru', 1500, 1400),
    ('Mankessim / Saltpond', 'Mankessim / Saltpond', 1600, 1550),
    ('Anomabo', 'Anomabo', 1600, 1550),
    ('Cape Coast', 'Cape Coast', 1700, 1650),
    ('Assin Fosu Areas', 'Assin Fosu Areas', 1800, 1750),
    ('Elmina Areas', 'Elmina Areas', 1800, 1750),
    # Eastern Region
    ('Aburi', 'Aburi', 1500, 1500),
    ('Nkawkaw / Kwahu', 'Nkawkaw / Kwahu', 1700, 1600),
    ('Akosombo', 'Akosombo', 1600, 1500),
    ('Somanya', 'Somanya', 1500, 1450),
    ('Nsawam', 'Nsawam', 1500, 1450),
    ('Kwabeng', 'Kwabeng', 1600, 1500),
    ('Oda / Koforidua / Kyebi', 'Oda / Koforidua / Kyebi', 1700, 1600),
    ('Afram Plains / Donkorkrom', 'Afram Plains / Donkorkrom', 2200, 2050),
    # Volta Region
    ('Southern Volta Areas', 'Southern Volta Areas', 1800, 1750),
    ('Northern Volta Areas', 'Northern Volta Areas', 2200, 2000),
    # Western Region
    ('Takoradi', 'Takoradi', 2200, 2000),
    ('Axim Areas', 'Axim Areas', 2700, 2500),
    ('Western North / Sefwi Areas', 'Western North / Sefwi Areas', 3000, 2800),
    ('Tarkwa', 'Tarkwa', 3000, 2800),
    # Bono Region
    ('Sunyani', 'Sunyani', 3000, 2800),
    ('Kintampo', 'Kintampo', 3000, 2800),
    # Ashanti Region
    ('Kumasi', 'Kumasi', 2200, 2000),
    # Northern Region
    ('Northern Region', 'Northern Region', 3700, 3550),
]

# Build dropdown choices
BUS_DESTINATIONS = [('', 'Select Destination')] + [(d[0], d[1]) for d in BUS_DESTINATIONS_DATA]

# Build price lookup: { destination: { bus_type: price } }
BUS_PRICE_MAP = {}
for dest, label, coaster, hiace in BUS_DESTINATIONS_DATA:
    BUS_PRICE_MAP[dest] = {
        'Coaster Bus': coaster,
        'Hiace Mini Bus': hiace,
    }

BUS_TYPES = [
    ('', 'Select Bus Type'),
    ('Coaster Bus', 'Coaster Bus'),
    ('Hiace Mini Bus', 'Hiace Mini Bus'),
]

TRIP_TYPES = [
    ('one_way', 'One Way'),
    ('round_trip', 'Round Trip'),
]

# Pickup locations for the search widget
PICKUP_LOCATIONS = [
    ('', 'Select Pick-up Location'),
    ('Accra', 'Accra'),
    ('Tema', 'Tema'),
    ('Kumasi', 'Kumasi'),
    ('Takoradi', 'Takoradi'),
    ('Cape Coast', 'Cape Coast'),
    ('Tamale', 'Tamale'),
    ('Koforidua', 'Koforidua'),
    ('Ho', 'Ho'),
    ('Sunyani', 'Sunyani'),
]

# Fleet: actual bus models grouped by pricing tier
BUS_MODELS = [
    {
        'id': 'toyota-hiace',
        'name': 'Toyota Hiace',
        'tier': 'Hiace Mini Bus',
        'category': 'Mini Bus',
        'seats': 15,
        'luggage': 10,
        'transmission': 'Manual',
        'ac': True,
        'icon': 'fa-shuttle-van',
        'image': None,
        'features': ['Air Conditioning', 'Reclining Seats', 'Driver Included', 'Fuel Included'],
        'description': 'Compact and reliable. Perfect for small groups, family trips, and corporate outings.',
    },
    {
        'id': 'mercedes-sprinter',
        'name': 'Mercedes-Benz Sprinter',
        'tier': 'Hiace Mini Bus',
        'category': 'Mini Bus',
        'seats': 16,
        'luggage': 12,
        'transmission': 'Manual',
        'ac': True,
        'icon': 'fa-shuttle-van',
        'image': None,
        'features': ['Air Conditioning', 'Premium Interior', 'Driver Included', 'Fuel Included'],
        'description': 'Premium European comfort for small groups. Smooth ride and quiet cabin.',
    },
    {
        'id': 'toyota-coaster',
        'name': 'Toyota Coaster',
        'tier': 'Coaster Bus',
        'category': 'Coach',
        'seats': 30,
        'luggage': 20,
        'transmission': 'Manual',
        'ac': True,
        'icon': 'fa-bus',
        'image': '/static/img/buses/coaster.jpg',
        'features': ['Air Conditioning', 'Overhead Storage', 'Driver Included', 'Fuel Included'],
        'description': 'Reliable mid-size coach. Ideal for church trips, school excursions and events.',
    },
    {
        'id': 'yutong-coach',
        'name': 'Yutong Coach',
        'tier': 'Coaster Bus',
        'category': 'Coach',
        'seats': 35,
        'luggage': 25,
        'transmission': 'Automatic',
        'ac': True,
        'icon': 'fa-bus-alt',
        'image': '/static/img/buses/yutong.jpg',
        'features': ['Air Conditioning', 'Reclining Seats', 'Driver Included', 'Fuel Included'],
        'description': 'Modern Chinese-built coach. Automatic transmission and spacious luggage hold.',
    },
    {
        'id': 'mercedes-tourismo',
        'name': 'Mercedes-Benz Tourismo',
        'tier': 'Coaster Bus',
        'category': 'Luxury Coach',
        'seats': 45,
        'luggage': 35,
        'transmission': 'Automatic',
        'ac': True,
        'icon': 'fa-bus-alt',
        'image': '/static/img/buses/tourismo.jpg',
        'features': ['Premium AC', 'Reclining Seats', 'Driver Included', 'Fuel Included', 'On-Board Restroom'],
        'description': 'Our flagship luxury coach. Perfect for weddings, conferences, and long-distance travel.',
    },
]


def get_bus_model(model_id):
    for m in BUS_MODELS:
        if m['id'] == model_id:
            return m
    return None


# Optional extras added at checkout
BUS_EXTRAS = [
    {'id': 'refreshments', 'name': 'Refreshments Package', 'description': 'Bottled water and light snacks for all passengers', 'price': 150},
    {'id': 'extended_hours', 'name': 'Extended Hours', 'description': 'Additional hours beyond standard 12-hour day rate', 'price': 300},
    {'id': 'priority_support', 'name': 'Priority Support', 'description': '24/7 dedicated hotline during your trip', 'price': 100},
    {'id': 'additional_stop', 'name': 'Additional Pickup Stop', 'description': 'One extra pickup point along the way', 'price': 200},
]


def get_bus_extra(extra_id):
    for e in BUS_EXTRAS:
        if e['id'] == extra_id:
            return e
    return None


def calculate_bus_total(model_id, destinations, trip_type='one_way', days=1, extras=None):
    model = get_bus_model(model_id)
    if not model:
        return 0
    base = 0
    for dest in destinations:
        base += BUS_PRICE_MAP.get(dest, {}).get(model['tier'], 0)
    if trip_type == 'round_trip':
        base *= 2
    base *= max(days, 1)
    if extras:
        for extra_id in extras:
            extra = get_bus_extra(extra_id)
            if extra:
                base += extra['price']
    return base


def get_bus_price(destination, bus_type, trip_type='one_way', days=1):
    base = BUS_PRICE_MAP.get(destination, {}).get(bus_type, 0)
    if trip_type == 'round_trip':
        base = base * 2
    return base * days


# --- Apartment ---

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

APARTMENT_PRICES = {
    'Studio': 200,
    '1-Bedroom': 280,
    '2-Bedroom': 350,
    '3-Bedroom': 450,
}

def get_apartment_price(apartment_type):
    return APARTMENT_PRICES.get(apartment_type, 250)


# --- Tours ---

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

TOUR_PRICES = {'default': 500}


# --- Forms ---

class ContactForm(FlaskForm):
    name = StringField("NAME", validators=[DataRequired('A full name is required'), Length(min=5, max=30)])
    email = StringField("EMAIL", validators=[DataRequired('A correct email is required'), Email()])
    subject = StringField("SUBJECT", validators=[DataRequired('A subject is required')])
    message = TextAreaField("MESSAGE", validators=[DataRequired('A message is required'), Length(min=5, max=500)])
    submit = SubmitField("SEND")


class BusSearchForm(FlaskForm):
    trip_type = SelectField('Trip Type', choices=TRIP_TYPES, default='one_way', validators=[DataRequired()])
    pickup_location = SelectField('Pick-up Location', choices=PICKUP_LOCATIONS, validators=[DataRequired('Please select a pick-up location')])
    travel_date = StringField('Travel Date', validators=[DataRequired('Please select a travel date')])
    return_date = StringField('Return Date', validators=[Optional()])
    days = IntegerField('Number of Days', validators=[DataRequired(), NumberRange(min=1, max=30)])
    submit = SubmitField('Search Buses')


class BusCheckoutForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired('Please enter your full name'), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired('Please enter your email'), Email()])
    phone = StringField('Phone', validators=[DataRequired('Please enter your phone number'), Length(min=7, max=20)])
    submit = SubmitField('Complete Booking')


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
