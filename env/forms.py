from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email
from wtforms import DateField 
import email_validator


class ContactForm(FlaskForm):

    name = StringField("NAME", validators=[DataRequired('A full name is required'), Length(min=5, max=30)])
    email = StringField("EMAIL", validators=[DataRequired('A correct email is required'), Email()])
    subject = StringField("SUBJECT", validators=[DataRequired('A subject is required')])
    message = TextAreaField("MESSAGE", validators=[DataRequired('A message is required'), Length(min=5, max=500)])
    submit = SubmitField("SEND")


class BookingForm(FlaskForm):
    destination = SelectField(
        'Destination',
        choices=[
            ('1', 'Aburi Botanical Gardens'),
            ('2', 'Accra Zoo'),
            ("3", 'Ada Foah Beach'),
            ("4", 'Ankasa Forest'),
            ("5", 'Bobiri Forest and Butterfly Sanctuary'),
            ("6", 'Boabeng Fiema Monkey Sanctuary'),
            ("7", 'Bunsu Arboretum'),
            ("8", 'Buoyam Caves'),
            ("9", 'Cape Coast Castle'),
            ("10", 'Cape Three Point'),
            ("11", 'Dubois Memorial Centre'),
            ("12", 'Elmina Castle'),
            ("13", 'Gemi Amedzofe(Mountain)'),
            ("14", 'Ghana Museum'),
            ("15", 'Kakum National Park'),
            ("16", 'Kintampo Waterfalls'),
            ("17", 'Kumasi Armed Forces Military Museum'),
            ("18", 'Kumasi Zoo'),
            ("19", 'Kyabobo National Park'),
            ("20", 'Manhyia Palace'),
            ("21", 'Mole National Park'),
            ("22", 'Mognori Eco Village'),
            ("23", 'Mountain Afadjato(Tagbo Waterfall)'),
            ("24", 'Nkrumah Memorial Park'),
            ("25", 'Nzulezu Stilt Village'),
            ("26", 'Obuasi Mine'),
            ("27", 'Okomfo Anokye Sword'),
            ("28", 'Paga Chief Pond'),
            ("29", 'Paga Zenga Crocodile Pond'),
            ("30", 'Pikworo Nania Slave Camp'),
            ("31", 'Prempeh Jubilee'),
            ("32", 'Shai Hills'),
            ("33", 'Sirigu Women Organisation for Pottery Art'),
            ("34", 'Tagbo Waterfall/Mountain Afadjato'),
            ("35", 'Tafi Atome Monkey Sanctuary'),
            ("36", 'Tango Hills/Tingzag Shrine'),
            ("37", 'Tano Boase Sacred Grove'),
            ("38", 'Wassa Domama Roch Shrine'),
            ("39", 'Wechiau Hippo Sanctuary'),
            ("40", 'Wli Waterfalls'),
            ("41", 'Xavi Bird Sanctuary'),
            ("42", 'Destination 1'),
            ("43", 'Destination 1'),
            ("44", 'Destination 1'),
            ("45", 'Destination 1'),
            ("46", 'Destination 1'),
            ("47", 'Destination 1'),
            ("48", 'Destination 1'),
            ("49", 'Destination 1'),
            ("50", 'Destination 1')
        ],
        validators=[DataRequired()]
    )

    depart_date = DateField(
        'Depart Date',
        format='%Y-%m-%d',  # Adjust the format as needed
        validators=[DataRequired()]
    )

    return_date = DateField(
        'Return Date',
        format='%Y-%m-%d',  # Adjust the format as needed
        validators=[DataRequired()]
    )

    duration = SelectField(
        'Duration',
        choices=[
            ('1', 'Duration 1'),
            ('2', 'Duration 2'),
            ('3', 'Duration 3')
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField('Submit')

