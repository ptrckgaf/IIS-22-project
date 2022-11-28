from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, widgets, BooleanField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from iis_wis2.models import User, UserType, CourseType, CourseLanguage
from sqlalchemy.orm import sessionmaker
from iis_wis2 import engine


class RegisterForm(FlaskForm):
    def validate_login(self, login_to_check):
        Session = sessionmaker(engine)
        with Session() as session:
            login = session.query(User).filter_by(login=login_to_check.data).first()
        if login:
            raise ValidationError('Login already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        Session = sessionmaker(engine)
        with Session() as session:
            email_address = session.query(User).filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    login = StringField(label='Login:', validators=[Length(min=2, max=30), DataRequired()])
    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    user_type = SelectField(label='User Type:', validators=[DataRequired()],
                            choices=[user_type.name for user_type in UserType])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')


class UserAccountForm(FlaskForm):
    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Uložit')


class CourseCreateForm(FlaskForm):
    name = StringField(label='Název:', validators=[Length(min=2, max=30), DataRequired()])
    course_type = SelectField(label='Typ kurzu:', validators=[DataRequired()],
                            choices=[course_type.value for course_type in CourseType])
    language = SelectField(label='Jazyk kurzu:', validators=[DataRequired()],
                           choices=[language.value for language in CourseLanguage])
    description = StringField(label='Popis:', validators=[Length(min=0, max=1024), DataRequired()])
    credits = IntegerField(label='Počet kreditov:', validators=[DataRequired()])
    users_limit = IntegerField(label='Limit kurzu:', validators=[DataRequired()])
    submit = SubmitField(label='Odeslat žádost o registraci kurzu')


class CourseRegistrationForm(FlaskForm):
    submit = SubmitField(label='Schválit vybrané žádosti o registraci')

class CoursesToConfirmForm(FlaskForm):
    submit = SubmitField(label='Schválit vybrané kurzy')


class GuaranteedCoursesForm(FlaskForm):
    submit = SubmitField(label='Uložit')


class MyCoursesForm(FlaskForm):
    submit = SubmitField(label='Zrušit registraci')


class CoursesForm(FlaskForm):
    submit = SubmitField(label='Odeslat žádost o registraci na vybrané kurzy')


class TermsForm(FlaskForm):
    submit = SubmitField(label='Registrovat')

class CoursesDetailsForm(FlaskForm):
    name = StringField(label='Název:', validators=[Length(min=2, max=30), DataRequired()])
    course_language = StringField(label='Jazyk:', validators=[DataRequired()])
    course_type = SelectField(label='Typ kurzu:', validators=[DataRequired()],
                              choices=[course_type.name for course_type in CourseType])
    description = StringField(label='Popis:', validators=[Length(min=0, max=1024), DataRequired()])
    price = IntegerField(label='Cena kurzu:', validators=[DataRequired()])
    users_limit = IntegerField(label='Limit kurzu:', validators=[DataRequired()])
    submit = SubmitField(label='Uložit')


class LoginForm(FlaskForm):
    login = StringField(label='Login:', validators=[DataRequired()])
    password = PasswordField(label='Heslo:', validators=[DataRequired()])
    submit = SubmitField(label='Přihlásit')
