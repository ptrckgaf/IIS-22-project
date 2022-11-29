from iis_wis2 import app, engine
from flask import render_template, redirect, url_for, flash, request
from iis_wis2.models import User, Course, UserType, UsersHaveRegisteredCourses, Term, Room, UsersHaveRegisteredTerms
from iis_wis2.forms import RegisterForm, LoginForm, CoursesForm, MyCoursesForm, UserAccountForm, CourseCreateForm, \
    CoursesToConfirmForm, CourseEditForm, CourseRegistrationForm, TermsForm, UsersForm, RoomCreateForm, RoomsForm, \
    RoomEditForm, DeletingUserFromCourseForm, CourseTeacherRegistrationForm, DeletingTeacherFromCourseForm, \
    TermCreateForm, TermsInCourseForm, StudentsInTermForm, StudentsEvaluationInTermForm, \
    TermRegisterForm, TermUnregisterForm
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
            flash(f'Přihlášení proběhlo úspěšně. Jste přihlášen jako: {attempted_user.login}', category='success')

            if attempted_user.user_type != UserType.administrator:
                return redirect(url_for('courses_page'))

            return redirect(url_for('user_create_page'))
        else:
            flash('Špatně zadaný login nebo heslo.', category='danger')

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


@app.route('/admin_courses', methods=['GET', 'POST'])
def admin_courses_page():
    Session = sessionmaker(engine)
    with Session() as session:
        courses = session.query(Course).all()
        return render_template('admin_courses.html', courses=courses)


@app.route('/user_account_page', methods=['GET', 'POST'])
def user_account_page():
    Session = sessionmaker(engine)
    user_account_form = UserAccountForm()

    if request.method == "POST":
        if user_account_form.validate_on_submit():
            with Session() as session:
                db_user = session.query(User).filter_by(id=current_user.id).first()
                new_email_address = user_account_form.email_address.data
                old_email_address = db_user.email_address

                # ve formuláři byla zadána nová adresa
                if old_email_address != new_email_address:
                    db_user_with_new_email_address = session.query(User).filter_by(
                        email_address=new_email_address).first()

                    if db_user_with_new_email_address:
                        # již existuje uživatel s emailovou adresou
                        flash(f'Emailová adresa již existuje: {new_email_address}', category='danger')
                    else:
                        # emailová adresa neexistuje a můžeme ji tedy aktualizovat
                        db_user.email_address = new_email_address

                db_user.username = user_account_form.username.data
                session.commit()
                flash(f"Editace úspěšně provedena!", category='success')
                return redirect(url_for('user_account_page'))

    if request.method == "GET":
        with Session() as session:
            db_user = session.query(User).filter_by(id=current_user.id).first()
            user_account_form.username.data = db_user.username
            user_account_form.email_address.data = db_user.email_address
            return render_template('user_account.html', form=user_account_form)


@app.route('/room_create_page', methods=['GET', 'POST'])
def room_create_page():
    Session = sessionmaker(engine)
    room_create_form = RoomCreateForm()

    if request.method == "POST":
        if room_create_form.validate_on_submit():
            with Session() as session:
                room_to_create = Room(name=room_create_form.name.data,
                                      capacity=room_create_form.capacity.data)
                session.add(room_to_create)
                session.commit()
                flash(f"Nová místnost {room_to_create.name} úspěšně vytvořena!", category='success')
        return redirect(url_for('room_create_page'))

    if request.method == "GET":
        return render_template('room_create.html', form=room_create_form)

@app.route('/course_create_page', methods=['GET', 'POST'])
def course_create_page():
    Session = sessionmaker(engine)
    form = CourseCreateForm()
    if form.validate_on_submit():
        with Session() as session:
            course_to_create = Course(name=form.name.data,
                                course_type=form.course_type.data,
                                language=form.language.data,
                                description=form.description.data,
                                credit_count=form.credits.data,
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


@app.route('/user_create', methods=['GET', 'POST'])
def user_create_page():

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
            flash(f"Uživatel {user_to_create.username} úspěšně vytvořen!", category='success')
        return redirect(url_for('user_create_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'Chyba během vytváření uživatele: {err_msg}', category='danger')
    return render_template('user_create.html', form=form)


@app.route('/user_detail_page/<user_login>', methods=['GET', 'POST'])
def user_detail_page(user_login):
    user_account_form = UserAccountForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        if user_account_form.validate_on_submit():
            with Session() as session:
                db_user = session.query(User).filter_by(login=user_login).first()
                new_email_address = user_account_form.email_address.data
                old_email_address = db_user.email_address

                # ve formuláři byla zadána nová adresa
                if old_email_address != new_email_address:
                    db_user_with_new_email_address = session.query(User).filter_by(
                        email_address=new_email_address).first()

                    if db_user_with_new_email_address:
                        # již existuje uživatel s emailovou adresou
                        flash(f'Emailová adresa již existuje: {new_email_address}', category='danger')
                    else:
                        # emailová adresa neexistuje a můžeme ji tedy aktualizovat
                        db_user.email_address = new_email_address

                db_user.username = user_account_form.username.data
                session.commit()
                flash(f"Editace úspěšně provedena!", category='success')
                return redirect(url_for('user_detail_page', user_login=user_login))

    if user_account_form.errors != {}: #If there are not errors from the validations
        for err_msg in user_account_form.errors.values():
            flash(f'Chyba během editace uživatele: {err_msg}', category='danger')

    if request.method == "GET":
        with Session() as session:
            db_user = session.query(User).filter_by(login=user_login).first()
            user_account_form.username.data = db_user.username
            user_account_form.email_address.data = db_user.email_address
            return render_template('user_account.html', form=user_account_form)

@app.route('/student_course_administration_page/<course_name>', methods=['GET', 'POST'])
def student_course_administration_page(course_name):
    course_registration_form = CourseRegistrationForm()
    deleting_user_from_course_form_form = DeletingUserFromCourseForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        with Session() as session:
            if course_registration_form.validate_on_submit():
                confirmed_users_logins = [value for elem, value in request.form.items()
                                          if elem.startswith('confirmed_student_login')]

                db_users_course = session.query(UsersHaveRegisteredCourses). \
                    filter_by(course_name=course_name).all()

                for user_in_course in db_users_course:
                    if user_in_course.user.login in confirmed_users_logins:
                        user_in_course.registration_confirmed = True

                session.commit()

            if deleting_user_from_course_form_form.validate_on_submit():
                deleted_user_logins = [value for elem, value in request.form.items()
                                          if elem.startswith('deleted_user_login')]

                course = session.query(Course).filter_by(name=course_name).first()

                for student in course.users_in_course:
                    if student.login in deleted_user_logins:
                        course.users_in_course.remove(student)

                session.commit()

            return redirect(url_for('student_course_administration_page', course_name=course_name))

    if request.method == "GET":
        with Session() as session:
            course = session.query(Course).filter_by(name=course_name).first()

            confirmed_students_in_course = session.query(UsersHaveRegisteredCourses). \
                filter_by(course_name=course_name). \
                filter_by(registration_confirmed=True).all()

            confirmed_students_logins = [confirmed_student.user.login for confirmed_student
                                           in confirmed_students_in_course]

            unconfirmed_students_in_course = session.query(UsersHaveRegisteredCourses). \
                filter_by(course_name=course_name). \
                filter_by(registration_confirmed=False).all()

            unconfirmed_students_logins = [unconfirmed_student.user.login for unconfirmed_student
                                           in unconfirmed_students_in_course]

            return render_template('student_course_administration.html',
                                   course_name=course.name,
                                   course_registration_form=course_registration_form,
                                   unconfirmed_students_logins=unconfirmed_students_logins,
                                   confirmed_students_logins=confirmed_students_logins,
                                   deleting_user_from_course_form_form=deleting_user_from_course_form_form)


@app.route('/teacher_course_administration_page/<course_name>', methods=['GET', 'POST'])
def teacher_course_administration_page(course_name):
    course_teacher_registration_form = CourseTeacherRegistrationForm()
    deleting_teacher_from_course_form = DeletingTeacherFromCourseForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        with Session() as session:
            if course_teacher_registration_form.validate_on_submit():
                added_teachers_logins = [value for elem, value in request.form.items()
                                          if elem.startswith('added_teacher_login')]

                course = session.query(Course).filter_by(name=course_name).first()

                for login in added_teachers_logins:
                    added_teacher = session.query(User).filter_by(login=login).first()
                    course.teachers_in_course.append(added_teacher)

                session.commit()

            if deleting_teacher_from_course_form.validate_on_submit():
                deleted_teacher_logins = [value for elem, value in request.form.items()
                                          if elem.startswith('deleted_teacher_login')]

                course = session.query(Course).filter_by(name=course_name).first()

                for teacher in course.teachers_in_course:
                    if teacher.login in deleted_teacher_logins:
                        course.teachers_in_course.remove(teacher)

                session.commit()

            return redirect(url_for('teacher_course_administration_page', course_name=course_name))

    if request.method == "GET":
        with Session() as session:
            course = session.query(Course).filter_by(name=course_name).first()
            users = session.query(User).all()

            teachers_logins_in_course = [teacher.login for teacher in course.teachers_in_course]
            teachers_not_in_course = []
            for user in users:
                if user.login not in teachers_logins_in_course:
                    teachers_not_in_course.append(user)

            return render_template('teacher_course_administration.html',
                                   course_name=course.name,
                                   teachers_in_course=course.teachers_in_course,
                                   teachers_not_in_course=teachers_not_in_course,
                                   course_teacher_registration_form=course_teacher_registration_form,
                                   deleting_teacher_from_course_form=deleting_teacher_from_course_form)


@app.route('/term_create_page/<course_name>', methods=['GET', 'POST'])
def term_create_page(course_name):
    form = TermCreateForm()
    form.load_room_names()
    Session = sessionmaker(engine)

    if request.method == "POST":
        if form.validate_on_submit():
            with Session() as session:
                term_to_create = Term(name=form.name.data,
                                      type=form.type.data,
                                      maximum_points=form.maximum_points.data,
                                      date=form.date.data,
                                      start_time=form.start_time.data,
                                      end_time=form.end_time.data,
                                      course_name=course_name,
                                      room_name=form.room_name.data)
                session.add(term_to_create)
                session.commit()
                flash(f"Termín {term_to_create.name} úspěšně vytvořen!", category='success')

            return redirect(url_for('term_create_page', course_name=course_name))

        if form.errors != {}:  # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(f'Chyba při vytváření termínu: {err_msg}', category='danger')

    if request.method == "GET":
        return render_template('term_create.html', form=form, course_name=course_name)





















@app.route('/term_detail_page/<term_id>', methods=['GET', 'POST'])
def term_detail_page(term_id):
    students_evaluation_in_term_form = StudentsEvaluationInTermForm()
    students_in_term_form = StudentsInTermForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        if students_evaluation_in_term_form.validate_on_submit():
            with Session() as session:
                for login, obtained_points in request.form.items():
                    student = session.query(User).filter_by(login=login).first()
                    if student:
                        student_with_obtained_points = session.query(UsersHaveRegisteredTerms) \
                            .filter_by(term_id=term_id) \
                            .filter_by(user_id=student.id) \
                            .first()
                        student_with_obtained_points.obtained_points = obtained_points
                session.commit()

        if students_in_term_form.validate_on_submit():
            with Session() as session:
                term = session.query(Term).filter_by(id=term_id).first()
                deleted_students_logins = [value for elem, value in request.form.items()
                                               if elem.startswith('deleted_student_login')]
                for student in term.users_in_term:
                    if student.login in deleted_students_logins:
                        term.users_in_term.remove(student)
                session.commit()

        return redirect(url_for('term_detail_page', term_id=term_id))

    if request.method == "GET":
        with Session() as session:
            term = session.query(Term).filter_by(id=term_id).first()
            logins_with_obtained_points = {}

            for student_in_term in term.users_in_term:
                student_with_obtained_points = session.query(UsersHaveRegisteredTerms) \
                    .filter_by(term_id=term_id) \
                    .filter_by(user_id=student_in_term.id)\
                    .first()

                logins_with_obtained_points[student_in_term.login] = student_with_obtained_points.obtained_points

            return render_template('term_detail.html',
                                   students_evaluation_in_term_form=students_evaluation_in_term_form,
                                   students_in_term_form=students_in_term_form,
                                   students=logins_with_obtained_points)


@app.route('/terms_in_course_page/<course_name>', methods=['GET', 'POST'])
def terms_in_course_page(course_name):
    form = TermsInCourseForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        if form.validate_on_submit():
            with Session() as session:
                deleted_terms_ids = [value for elem, value in request.form.items()
                                          if elem.startswith('deleted_term_id')]

                course = session.query(Course).filter_by(name=course_name).first()

                for term in course.terms:
                    if str(term.id) in deleted_terms_ids:
                        course.terms.remove(term)

                session.commit()

            return redirect(url_for('terms_in_course_page', course_name=course_name))

    if request.method == "GET":
        with Session() as session:
            course = session.query(Course).filter_by(name=course_name).first()
            return render_template('terms_in_course.html', form=form, terms_in_course=course.terms,
                                   course_name=course_name)


class StudentCourseOverview:
    def __init__(self, login, email_address, obtained_points):
        self.login = login
        self.email_address = email_address
        self.obtained_points = obtained_points


@app.route('/course_overview_page/<course_name>', methods=['GET', 'POST'])
def course_overview_page(course_name):
    Session = sessionmaker(engine)

    with Session() as session:
        course = session.query(Course).filter_by(name=course_name).first()
        students_obtained_points = []

        for student in course.users_in_course:
            student_overview = StudentCourseOverview(student.login, student.email_address, 0)

            for term in course.terms:
                student_with_obtained_points = session.query(UsersHaveRegisteredTerms) \
                    .filter_by(term_id=term.id) \
                    .filter_by(user_id=student.id) \
                    .first()
                if student_with_obtained_points:
                    student_overview.obtained_points += student_with_obtained_points.obtained_points
            students_obtained_points.append(student_overview)

        return render_template('course_overview.html', students=students_obtained_points,
                               teachers=course.teachers_in_course)


@app.route('/course_edit_page/<course_name>', methods=['GET', 'POST'])
def course_edit_page(course_name):
    courses_edit_form = CourseEditForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        with Session() as session:
            if courses_edit_form.validate_on_submit():
                course = session.query(Course).filter_by(name=course_name).first()
                course.name = courses_edit_form.name.data
                course.course_type = courses_edit_form.course_type.data
                course.description = courses_edit_form.description.data
                course.price = courses_edit_form.price.data
                course.users_limit = courses_edit_form.users_limit.data
                session.commit()
                flash(f"Kurz {course.name} úspěšně editován!", category='success')

                if courses_edit_form.errors != {}: #If there are errors from the validations
                    for err_msg in courses_edit_form.errors.values():
                        flash(f'Chyba při eidtaci kurzu: {err_msg}', category='danger')

            return redirect(url_for('course_edit_page', course_name=course_name))

    if request.method == "GET":
        with Session() as session:
            course = session.query(Course).filter_by(name=course_name).first()
            courses_edit_form.name.data = course_name
            courses_edit_form.course_type.data = course.course_type
            courses_edit_form.description.data = course.description
            courses_edit_form.price.data = course.price
            courses_edit_form.users_limit.data = course.users_limit

        return render_template('course_edit.html', courses_edit_form=courses_edit_form, course_name=course.name)


@app.route('/course_detail_page/<course_name>', methods=['GET', 'POST'])
def course_detail_page(course_name):
    return "Not working"


@app.route('/users', methods=['GET', 'POST'])
def users_page():
    Session = sessionmaker(engine)
    users_form = UsersForm()

    if request.method == "POST":
        if users_form.validate_on_submit():
            with Session() as session:
                logins_of_users_to_delete = [value for elem, value in request.form.items()
                                               if elem.startswith('deleted_user_name')]

                for login in logins_of_users_to_delete:
                    deleted_user = session.query(User).filter_by(login=login).first()
                    session.delete(deleted_user)

                session.commit()
                return redirect(url_for('users_page'))

    if request.method == "GET":
        with Session() as session:
            users = session.query(User).all()
            if current_user.is_authenticated:
                return render_template('users.html', users=users, form=users_form)


@app.route('/rooms', methods=['GET', 'POST'])
def rooms_page():
    Session = sessionmaker(engine)
    rooms_form = RoomsForm()

    if request.method == "POST":
        if rooms_form.validate_on_submit():
            with Session() as session:
                names_of_rooms_to_delete = [value for elem, value in request.form.items()
                                               if elem.startswith('deleted_room_name')]

                for name in names_of_rooms_to_delete:
                    deleted_room = session.query(Room).filter_by(name=name).first()
                    session.delete(deleted_room)

                session.commit()
                return redirect(url_for('rooms_page'))

    if request.method == "GET":
        with Session() as session:
            rooms = session.query(Room).all()
            if current_user.is_authenticated:
                return render_template('rooms.html', rooms=rooms, form=rooms_form)


@app.route('/room_detail_page/<room_name>', methods=['GET', 'POST'])
def room_detail_page(room_name):
    room_edit_form = RoomEditForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        if room_edit_form.validate_on_submit():
            with Session() as session:
                db_room = session.query(Room).filter_by(name=room_name).first()
                db_room.capacity = room_edit_form.capacity.data
                session.commit()
                flash(f"Editace úspěšně provedena!", category='success')
                return redirect(url_for('room_detail_page', room_name=room_name))

    if room_edit_form.errors != {}: #If there are not errors from the validations
        for err_msg in room_edit_form.errors.values():
            flash(f'Chyba během editace místnosti: {err_msg}', category='danger')

    if request.method == "GET":
        with Session() as session:
            db_room = session.query(Room).filter_by(name=room_name).first()
            room_edit_form.capacity.data = db_room.capacity
            return render_template('room_edit.html', form=room_edit_form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("Odhlášení proběhlo úspěšně!", category='info')
    return redirect(url_for("home_page"))


class StudiedCourseOverview:
    def __init__(self, name, language, type, guarantor_login, credit_count, obtained_points, grade):
        self.name = name
        self.language = language
        self.type = type
        self.guarantor_login = guarantor_login
        self.credit_count = credit_count
        self.obtained_points = obtained_points
        self.grade = grade


def get_grade_by_optainded_points(obtained_points):
    if obtained_points < 50:
        return "F"
    elif 50 <= obtained_points <= 59:
        return "E"
    elif 60 <= obtained_points <= 69:
        return "D"
    elif 70 <= obtained_points <= 79:
        return "C"
    elif 80 <= obtained_points <= 89:
        return "B"
    else:
        return "A"


@app.route('/studied_courses_page', methods=['GET', 'POST'])
def studied_courses_page():
    Session = sessionmaker(engine)
    with Session() as session:
        courses_overviews = []
        db_user = session.query(User).filter_by(id=current_user.id).first()

        for course in db_user.registered_courses:
            studied_course_overview = StudiedCourseOverview(course.name, course.language, course.course_type,
                                                            course.course_guarantor.login, course.credit_count,
                                                            0, "F")

            for term in course.terms:
                student_with_obtained_points = session.query(UsersHaveRegisteredTerms) \
                    .filter_by(term_id=term.id) \
                    .filter_by(user_id=current_user.id) \
                    .first()

                if student_with_obtained_points:
                    studied_course_overview.obtained_points += student_with_obtained_points.obtained_points

            courses_overviews.append(studied_course_overview)

        #grade update
        for course_overview in courses_overviews:
            course_overview.grade = get_grade_by_optainded_points(course_overview.obtained_points)

        return render_template('studied_courses.html', courses=courses_overviews)


class RegisteredTermOverview:
    def __init__(self, term, obtained_points):
        self.term = term
        self.obtained_points = obtained_points


@app.route('/term_registration_page/<course_name>', methods=['GET', 'POST'])
def term_registration_page(course_name):
    term_register_form = TermRegisterForm()
    term_unregister_form = TermUnregisterForm()
    Session = sessionmaker(engine)

    if request.method == "POST":
        if term_register_form.validate_on_submit():
            with Session() as session:
                ids_of_terms_to_register = [value for elem, value in request.form.items()
                                               if elem.startswith('registered_term_id')]
                user_db = session.query(User).filter_by(id=current_user.id).first()
                user_db.registered_terms.clear()

                for term_id in ids_of_terms_to_register:
                    registered_term = session.query(Term).filter_by(id=term_id).first()
                    user_db.registered_terms.append(registered_term)

                session.commit()
                return redirect(url_for('term_registration_page', course_name=course_name))

        if term_unregister_form.validate_on_submit():
            with Session() as session:
                ids_of_terms_to_register = [value for elem, value in request.form.items()
                                               if elem.startswith('unregistered_term_id')]
                user_db = session.query(User).filter_by(id=current_user.id).first()

                for term_id in ids_of_terms_to_register:
                    registered_term = session.query(Term).filter_by(id=term_id).first()
                    user_db.registered_terms.remove(registered_term)

                session.commit()
                return redirect(url_for('term_registration_page', course_name=course_name))

    if request.method == "GET":
        registered_terms_overviews = []

        with Session() as session:
            course = session.query(Course).filter_by(name=course_name).first()
            db_user = session.query(User).filter_by(id=current_user.id).first()

            for registered_term in db_user.registered_terms:
                registered_term_info = session.query(UsersHaveRegisteredTerms)\
                    .filter_by(user_id=current_user.id)\
                    .filter_by(term_id=registered_term.id)\
                    .first()
                registered_term_overview = RegisteredTermOverview(registered_term, registered_term_info.obtained_points)
                registered_terms_overviews.append(registered_term_overview)

            non_registered_terms = []

            for course_term in course.terms:
                if not course_term in db_user.registered_terms:
                    non_registered_terms.append(course_term)


            return render_template('term_registration.html', term_register_form=term_register_form,
                               term_unregister_form=term_unregister_form, terms=non_registered_terms,
                                   registered_terms_overviews=registered_terms_overviews)


@app.route('/taught_courses_page', methods=['GET', 'POST'])
def taught_courses_page():
    Session = sessionmaker(engine)
    with Session() as session:
        db_user = session.query(User).filter_by(id=current_user.id).first()
        return render_template('admin_courses.html', courses=db_user.teacher_in_courses)


@app.route('/guaranteed_courses_page', methods=['GET', 'POST'])
def guaranteed_courses_page():
    Session = sessionmaker(engine)

    if request.method == "GET":
        with Session() as session:
            db_user = session.query(User).filter_by(id=current_user.id).first()
            return render_template('admin_courses.html', courses=db_user.guarantor_of_courses)
