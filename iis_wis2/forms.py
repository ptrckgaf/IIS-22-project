from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, widgets, BooleanField, \
    IntegerField
from wtforms.fields import TimeField, DateField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from iis_wis2.models import User, UserType, CourseType, CourseLanguage, TermType, Room
from sqlalchemy.orm import sessionmaker
from iis_wis2 import engine
from datetime import date


class RegisterForm(FlaskForm):
    def validate_login(self, login_to_check):
        Session = sessionmaker(engine)
        with Session() as session:
            login = session.query(User).filter_by(login=login_to_check.data).first()
        if login:
            raise ValidationError('Zadaný login existuje! Zvolte prosím jiný.')

    def validate_email_address(self, email_address_to_check):
        Session = sessionmaker(engine)
        with Session() as session:
            email_address = session.query(User).filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Zadaná emailová adresa existuje! Zvolte prosím jinou.')

    login = StringField(label='Login:', validators=[Length(min=2, max=30), DataRequired()])
    username = StringField(label='Jméno:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email:', validators=[Email(), DataRequired()])
    user_type = SelectField(label='Typ:', validators=[DataRequired()],
                            choices=[user_type.name for user_type in UserType])
    password1 = PasswordField(label='Heslo:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Potvrzení hesla:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Vytvořit uživatele')


class UserAccountForm(FlaskForm):
    username = StringField(label='Jméno:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email:', validators=[Email(), DataRequired()])
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


class CoursesToConfirmForm(FlaskForm):
    submit = SubmitField(label='Schválit vybrané kurzy')


class GuaranteedCoursesForm(FlaskForm):
    submit = SubmitField(label='Uložit')


class UsersForm(FlaskForm):
    submit = SubmitField(label='Odstranit vybrané uživatele ze systému')


class RoomsForm(FlaskForm):
    submit = SubmitField(label='Odstranit vybrané místnosti ze systému')


class MyCoursesForm(FlaskForm):
    submit = SubmitField(label='Zrušit registraci')


class CoursesForm(FlaskForm):
    submit = SubmitField(label='Odeslat žádost o registraci na vybrané kurzy')


class TermsForm(FlaskForm):
    submit = SubmitField(label='Registrovat')

class CourseEditForm(FlaskForm):
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


class RoomCreateForm(FlaskForm):
    name = StringField(label='Název:', validators=[DataRequired()])
    capacity = IntegerField(label='Kapacita:', validators=[DataRequired()])
    submit = SubmitField(label='Vytvořit místnost')


class RoomEditForm(FlaskForm):
    capacity = IntegerField(label='Kapacita:', validators=[DataRequired()])
    submit = SubmitField(label='Uložit')


class CourseRegistrationForm(FlaskForm):
    submit = SubmitField(label='Schválit vybrané žádosti o registraci')


class DeletingUserFromCourseForm(FlaskForm):
    submit = SubmitField(label='Odstranit vybrané uživatele z kurzu')


class CourseTeacherRegistrationForm(FlaskForm):
    submit = SubmitField(label='Přidat vybrané učitele do kurzu')


class DeletingTeacherFromCourseForm(FlaskForm):
    submit = SubmitField(label='Odstranit vybrané učitele z kurzu')


class TermsInCourseForm(FlaskForm):
    submit = SubmitField(label='Odstranit vybrané termíny z kurzu')


class StudentsEvaluationInTermForm(FlaskForm):
    submit = SubmitField(label='Uložit hodnocení')


class StudentsInTermForm(FlaskForm):
    submit = SubmitField(label='Odstranit studenty z termínu')


class TermCreateForm(FlaskForm):
    name = StringField(label='Název:', validators=[DataRequired()])
    type = SelectField(label='Typ:', validators=[DataRequired()],
                            choices=[term_type.name for term_type in TermType])
    maximum_points = IntegerField(label='Maximální počet bodů:', validators=[DataRequired()])
    date = DateField(label='Datum:', format='%Y-%m-%d', default=date.today(), validators=[DataRequired()])
    start_time = TimeField(label='Čas začátku:', validators=[DataRequired()])
    end_time = TimeField(label='Čas konce:', validators=[DataRequired()])

    Session = sessionmaker(engine)
    with Session() as session:
        rooms = session.query(Room).all()
        room_name = SelectField(label='Název místnosti:', validators=[DataRequired()],
                            choices=[room.name for room in rooms])

    submit = SubmitField(label='Vytvořit termín')
