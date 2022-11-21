from iis_wis2 import app, engine
from flask import render_template, redirect, url_for, flash, request
from iis_wis2.models import User, Course, UserType, UsersHaveRegisteredCourses
from iis_wis2.forms import RegisterForm, LoginForm, CoursesForm, MyCoursesForm, UserAccountForm, CourseCreateForm, \
    CoursesToConfirmForm, CoursesDetailsForm, CourseRegistrationForm
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import sessionmaker


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home_page():

    if current_user.is_authenticated:
        return redirect(url_for('courses_page'))

    form = LoginForm()
    if form.validate_on_submit():
        Session = sessionmaker(engine)
        with Session() as session:
            attempted_user = session.query(User).filter_by(login=form.login.data).first()

        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.login}', category='success')

            if attempted_user.user_type != UserType.administrator:
                return redirect(url_for('courses_page'))

            return redirect(url_for('register_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/courses_to_confirm', methods=['GET', 'POST'])
def courses_to_confirm_page():
    Session = sessionmaker(engine)
    courses_to_confirm_form = CoursesToConfirmForm()

    if request.method == "POST":
        with Session() as session:
            courses = session.query(Course).filter_by(confirmed=False).all()
            names_of_courses_to_confirm = [value for elem, value in request.form.items()
                                  if elem.startswith('registered_course_name')]

            for course in courses:
                if course.name in names_of_courses_to_confirm:
                    course.confirmed = True

            session.commit()
            return redirect(url_for('courses_to_confirm_page'))

    if request.method == "GET":
        with Session() as session:
            courses = session.query(Course).all()
            return render_template('courses_to_confirm.html', courses=courses, form=courses_to_confirm_form)


@app.route('/courses', methods=['GET', 'POST'])
def courses_page():
    Session = sessionmaker(engine)
    courses_form = CoursesForm()

    if request.method == "POST":
        with Session() as session:
            db_user = session.query(User).filter_by(id=current_user.id).first()
            courses = session.query(Course).all()
            db_user.registered_courses.clear()
            registered_courses = [value for elem, value in request.form.items()
                                  if elem.startswith('registered_course_name')]

            for course in courses:
                if course.name in registered_courses:
                    db_user.registered_courses.append(course)

            session.commit()
            return redirect(url_for('courses_page'))

    if request.method == "GET":
        with Session() as session:
            courses = session.query(Course).all()
            if current_user.is_authenticated:
                db_user = session.query(User).filter_by(id=current_user.id).first()
                registered_courses_names = [course.name for course in db_user.registered_courses]
                return render_template('courses.html', courses=courses, form=courses_form,
                                       registered_courses_names=registered_courses_names)
            else:
                return render_template('courses.html', courses=courses, form=courses_form)


@app.route('/user_account_page', methods=['GET', 'POST'])
def user_account_page():
    Session = sessionmaker(engine)
    user_account_form = UserAccountForm()

    if request.method == "POST":
        if user_account_form.validate_on_submit():
            with Session() as session:
                db_user = session.query(User).filter_by(id=current_user.id).first()

                # ve formuláři byla zadána nová adresa
                if current_user.email_address != user_account_form.email_address.data:
                    db_email_address = session.query(User).\
                        filter_by(email_address=user_account_form.email_address.data).first()

                    if db_email_address:
                        # emailová adresa již exituje
                        flash(f'Emailová adresa již existuje: {db_email_address}', category='danger')
                    else:
                        # emailová adresa neexistuje a můžeme ji tedy aktualizovat
                        db_user.email_address = user_account_form.email_address.data

                db_user.username = user_account_form.username.data
                session.commit()
                return redirect(url_for('user_account_page'))

    if request.method == "GET":
        with Session() as session:
            db_user = session.query(User).filter_by(id=current_user.id).first()
            user_account_form.username.data = db_user.username
            user_account_form.email_address.data = db_user.email_address
            return render_template('user_account.html', form=user_account_form)

@app.route('/course_create_page', methods=['GET', 'POST'])
def course_create_page():
    Session = sessionmaker(engine)
    form = CourseCreateForm()
    if form.validate_on_submit():
        with Session() as session:
            course_to_create = Course(name=form.name.data,
                                course_type=form.course_type.data,
                                description=form.description.data,
                                price=form.price.data,
                                course_guarantor_id=current_user.id,
                                users_limit=form.users_limit.data,
                                confirmed=False)
            session.add(course_to_create)
            session.commit()
            flash(f"Žádost o vytvoření kurzu {course_to_create.name} úspěšně odeslána!", category='success')
        return redirect(url_for('course_create_page'))
    if form.errors != {}: #If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'Chyba při vytváření kurzu: {err_msg}', category='danger')

    return render_template('course_create.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():

    if current_user and current_user.user_type != UserType.administrator:
        return

    Session = sessionmaker(engine)
    form = RegisterForm()
    if form.validate_on_submit():
        with Session() as session:
            user_to_create = User(login=form.login.data,
                                username=form.username.data,
                                email_address=form.email_address.data,
                                user_type=form.user_type.data,
                                password=form.password1.data)
            session.add(user_to_create)
            session.commit()
            flash(f"User {user_to_create.username} created successfully!", category='success')
        return redirect(url_for('register_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/guaranteed_courses_page', methods=['GET', 'POST'])
def guaranteed_courses_page():
    Session = sessionmaker(engine)

    if request.method == "GET":
        with Session() as session:
            courses = session.query(Course).all()
            return render_template('guaranteed_courses.html', courses=courses)


@app.route('/course_detail_page/<course_name>', methods=['GET', 'POST'])
def course_detail_page(course_name):
    courses_detail_form = CoursesDetailsForm()
    course_registration_form = CourseRegistrationForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        with Session() as session:
            if course_registration_form.validate_on_submit():

                confirmed_users_logins = [value for elem, value in request.form.items()
                                          if elem.startswith('confirmed_student_login')]

                db_users_course = session.query(UsersHaveRegisteredCourses).\
                    filter_by(course_name=course_name).all()

                for user_in_course in db_users_course:
                    if user_in_course.user.login in confirmed_users_logins:
                        user_in_course.registration_confirmed = True

                session.commit()

            if courses_detail_form.validate_on_submit():
                course = session.query(Course).filter_by(name=course_name).first()
                course.name = courses_detail_form.name.data
                course.course_type = courses_detail_form.course_type.data
                course.description = courses_detail_form.description.data
                course.price = courses_detail_form.price.data
                course.users_limit = courses_detail_form.users_limit.data
                session.commit()
                flash(f"Kurz {course.name} úspěšně editován!", category='success')

                if courses_detail_form.errors != {}: #If there are errors from the validations
                    for err_msg in courses_detail_form.errors.values():
                        flash(f'Chyba při eidtaci kurzu: {err_msg}', category='danger')

            return redirect(url_for('course_detail_page', course_name=course_name))

    if request.method == "GET":
        with Session() as session:
            course = session.query(Course).filter_by(name=course_name).first()
            courses_detail_form.name.data = course_name
            courses_detail_form.course_type.data = course.course_type
            courses_detail_form.description.data = course.description
            courses_detail_form.price.data = course.price
            courses_detail_form.users_limit.data = course.users_limit

            unconfirmed_student_in_course = session.query(UsersHaveRegisteredCourses).\
                filter_by(course_name=course_name).\
                filter_by(registration_confirmed=False).all()

            unconfirmed_students_logins = [unconfirmed_student.user.login for unconfirmed_student
                                           in unconfirmed_student_in_course]

        return render_template('course_detail.html', courses_detail_form=courses_detail_form, course_name=course.name,
                               course_registration_form=course_registration_form,
                               unconfirmed_students_logins=unconfirmed_students_logins)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))
