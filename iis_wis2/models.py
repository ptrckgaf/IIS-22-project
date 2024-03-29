import enum
from iis_wis2 import Base, login_manager, engine, bcrypt
from flask_login import UserMixin
from sqlalchemy import Enum, Column, Integer, String, Table, ForeignKey, Date, Boolean, Time
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker


class UserType(enum.Enum):
    administrator = 1
    user = 2


class CourseType(enum.Enum):
    compulsory = 1
    optional = 2


class TermType(enum.Enum):
    lecture = 1
    exercise = 2
    exam = 3


class CourseLanguage(enum.Enum):
    czech = 1
    english = 2


class DaysOfTheWeek(enum.Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(engine)
    with Session() as session:
        return session.query(User).filter_by(id=user_id).first()


users_teach_in_courses = Table(
    "users_teach_in_courses",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("course_name", ForeignKey("course.name"),  primary_key=True)
)


class UsersHaveRegisteredTerms(Base):
    __tablename__ = "users_have_registered_terms"
    user_id = Column(ForeignKey("user.id"), primary_key=True)
    term_id = Column(ForeignKey("term.id"),  primary_key=True)
    obtained_points = Column(Integer(), nullable=False, default=0)


class UsersHaveRegisteredCourses(Base):
    __tablename__ = "users_have_registered_courses"
    user_id = Column(ForeignKey("user.id"), primary_key=True)
    course_name = Column(ForeignKey("course.name"),  primary_key=True)
    registration_confirmed = Column(Boolean(), nullable=False, default=False)
    grade = Column(String(length=1), nullable=False, default="F")
    user = relationship('User', viewonly=True)


class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer(), primary_key=True)
    login = Column(String(length=30))
    username = Column(String(length=30), nullable=False)
    email_address = Column(String(length=50), nullable=False, unique=True)
    password_hash = Column(String(length=60), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    guarantor_of_courses = relationship('Course', backref='course_guarantor')
    registered_courses = relationship("Course", secondary="users_have_registered_courses",
                                      back_populates="users_in_course")
    registered_terms = relationship(
        "Term", secondary="users_have_registered_terms", back_populates="users_in_term")
    teacher_in_courses = relationship(
        "Course", secondary=users_teach_in_courses, back_populates="teachers_in_course")

    def __str__(self):
        return f'{self.login}'

    @property
    def is_admin(self):
        return self.user_type == UserType.administrator

    @property
    def is_user(self):
        return self.user_type == UserType.user


    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Course(Base, UserMixin):
    __tablename__ = "course"
    name = Column(String(length=30), primary_key=True)
    description = Column(String(length=1024))
    course_type = Column(Enum(CourseType), nullable=False)
    language = Column(Enum(CourseLanguage), nullable=False)
    credit_count = Column(Integer(), nullable=False)
    price = Column(Integer(), nullable=True)
    news = Column(String(length=1024))
    confirmed = Column(Boolean(), nullable=False)
    users_limit = Column(Integer(), nullable=False)
    day_of_the_week = Column(Enum(DaysOfTheWeek), nullable=True)
    start_time = Column(Time(), nullable=True)
    end_time = Column(Time(), nullable=True)
    course_guarantor_id = Column(Integer(), ForeignKey('user.id'), nullable=False)
    users_in_course = relationship(
        "User", secondary="users_have_registered_courses", back_populates="registered_courses")
    teachers_in_course = relationship(
        "User", secondary=users_teach_in_courses, back_populates="teacher_in_courses")
    terms = relationship('Term', backref='course')


class Term(Base, UserMixin):
    __tablename__ = "term"
    id = Column(Integer(), primary_key=True)
    name = Column(String(length=30), nullable=False)
    type = Column(Enum(TermType), nullable=False)
    maximum_points = Column(Integer(), nullable=False)
    description = Column(String(length=1024))
    date = Column(Date(), nullable=False)
    start_time = Column(Time(), nullable=False)
    end_time = Column(Time(), nullable=False)
    course_name = Column(String(length=30), ForeignKey('course.name'), nullable=True)
    room_name = Column(String(length=30), ForeignKey('room.name'), nullable=True)
    users_in_term = relationship(
        "User", secondary="users_have_registered_terms", back_populates="registered_terms")


class Room(Base, UserMixin):
    __tablename__ = "room"
    name = Column(String(length=30), primary_key=True)
    capacity = Column(Integer(), nullable=False)
    terms = relationship('Term', backref='room')
