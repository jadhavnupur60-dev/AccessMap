"""
database.py - Database models and initialization for AccessMap
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for registration and login"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)


class Facility(db.Model):
    """Facility model - stores accessible places"""
    __tablename__ = 'facilities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    description = db.Column(db.Text)

    wheelchair_accessible = db.Column(db.Boolean, default=False)
    has_ramp = db.Column(db.Boolean, default=False)
    has_accessible_toilet = db.Column(db.Boolean, default=False)
    has_elevator = db.Column(db.Boolean, default=False)
    has_accessible_parking = db.Column(db.Boolean, default=False)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    average_rating = db.Column(db.Float, default=0.0)

    reviews = db.relationship('Review', backref='facility', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='facility', lazy=True, cascade='all, delete-orphan')


class Review(db.Model):
    """Community reviews and ratings"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Report(db.Model):
    """Accessibility issue reports"""
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Feedback(db.Model):
    """User feedback"""
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def init_db(app):
    """Initialize database with sample data"""
    db.init_app(app)

    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@accessmap.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

            sample_facilities = [
                Facility(
                    name='City Central Library',
                    category='Library',
                    address='123 Main Street',
                    city='Mumbai',
                    latitude=19.0760,
                    longitude=72.8777,
                    description='Public library with full accessibility features',
                    wheelchair_accessible=True,
                    has_ramp=True,
                    has_accessible_toilet=True,
                    has_elevator=True,
                    has_accessible_parking=True,
                    created_by=1
                ),
                Facility(
                    name='Sunrise Shopping Mall',
                    category='Shopping',
                    address='45 Park Avenue',
                    city='Delhi',
                    latitude=28.6139,
                    longitude=77.2090,
                    description='Modern shopping mall with accessibility support',
                    wheelchair_accessible=True,
                    has_ramp=True,
                    has_accessible_toilet=True,
                    has_elevator=True,
                    has_accessible_parking=False,
                    created_by=1
                ),
                Facility(
                    name='Green Park Hospital',
                    category='Hospital',
                    address='78 Health Road',
                    city='Bangalore',
                    latitude=12.9716,
                    longitude=77.5946,
                    description='Multi-specialty hospital with wheelchair access',
                    wheelchair_accessible=True,
                    has_ramp=True,
                    has_accessible_toilet=True,
                    has_elevator=True,
                    has_accessible_parking=True,
                    created_by=1
                ),
                Facility(
                    name='Sunset Restaurant',
                    category='Restaurant',
                    address='12 Food Street',
                    city='Pune',
                    latitude=18.5204,
                    longitude=73.8567,
                    description='Family restaurant with partial accessibility',
                    wheelchair_accessible=True,
                    has_ramp=True,
                    has_accessible_toilet=False,
                    has_elevator=False,
                    has_accessible_parking=False,
                    created_by=1
                ),
                Facility(
                    name='Metro Station - Central',
                    category='Transport',
                    address='Central Square',
                    city='Chennai',
                    latitude=13.0827,
                    longitude=80.2707,
                    description='Metro station with elevator and ramp access',
                    wheelchair_accessible=True,
                    has_ramp=True,
                    has_accessible_toilet=True,
                    has_elevator=True,
                    has_accessible_parking=False,
                    created_by=1
                ),
            ]

            for facility in sample_facilities:
                db.session.add(facility)

            db.session.commit()
            print("✅ Database initialized with sample data!")