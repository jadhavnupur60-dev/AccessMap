"""
app.py - Main Flask application for AccessMap
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, init_db, User, Facility, Review, Report, Feedback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'accessmap-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accessmap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============ CLIENT ROUTES ============

@app.route('/')
def index():
    facilities = Facility.query.order_by(Facility.average_rating.desc()).limit(6).all()
    stats = {
        'facilities': Facility.query.count(),
        'reviews': Review.query.count(),
        'users': User.query.count(),
        'reports': Report.query.count()
    }
    return render_template('index.html', facilities=facilities, stats=stats)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/search')
def search():
    query = request.args.get('q', '')
    city = request.args.get('city', '')
    category = request.args.get('category', '')

    facilities = Facility.query

    if query:
        facilities = facilities.filter(Facility.name.contains(query))
    if city:
        facilities = facilities.filter(Facility.city.contains(city))
    if category:
        facilities = facilities.filter(Facility.category == category)

    results = facilities.all()
    cities = db.session.query(Facility.city).distinct().all()
    categories = db.session.query(Facility.category).distinct().all()

    return render_template('search.html',
                           facilities=results,
                           query=query,
                           cities=[c[0] for c in cities],
                           categories=[c[0] for c in categories])


@app.route('/facility/<int:facility_id>')
def facility_detail(facility_id):
    facility = Facility.query.get_or_404(facility_id)
    reviews = Review.query.filter_by(facility_id=facility_id).order_by(Review.created_at.desc()).all()
    return render_template('facility_detail.html', facility=facility, reviews=reviews)


@app.route('/add-facility', methods=['GET', 'POST'])
@login_required
def add_facility():
    if request.method == 'POST':
        facility = Facility(
            name=request.form.get('name'),
            category=request.form.get('category'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            latitude=float(request.form.get('latitude') or 0),
            longitude=float(request.form.get('longitude') or 0),
            description=request.form.get('description'),
            wheelchair_accessible='wheelchair_accessible' in request.form,
            has_ramp='has_ramp' in request.form,
            has_accessible_toilet='has_accessible_toilet' in request.form,
            has_elevator='has_elevator' in request.form,
            has_accessible_parking='has_accessible_parking' in request.form,
            created_by=current_user.id
        )
        db.session.add(facility)
        db.session.commit()

        flash('Facility added successfully!', 'success')
        return redirect(url_for('facility_detail', facility_id=facility.id))

    return render_template('add_facility.html')


@app.route('/report-issue/<int:facility_id>', methods=['GET', 'POST'])
@login_required
def report_issue(facility_id):
    facility = Facility.query.get_or_404(facility_id)

    if request.method == 'POST':
        report = Report(
            facility_id=facility_id,
            user_id=current_user.id,
            issue_type=request.form.get('issue_type'),
            description=request.form.get('description')
        )
        db.session.add(report)
        db.session.commit()

        flash('Report submitted successfully!', 'success')
        return redirect(url_for('facility_detail', facility_id=facility_id))

    return render_template('report_issue.html', facility=facility)


@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        fb = Feedback(
            user_id=current_user.id,
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )
        db.session.add(fb)
        db.session.commit()

        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('index'))

    return render_template('feedback.html')


@app.route('/profile')
@login_required
def profile():
    user_reviews = Review.query.filter_by(user_id=current_user.id).all()
    user_reports = Report.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', reviews=user_reviews, reports=user_reports)


@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied! Admin only.', 'danger')
        return redirect(url_for('index'))

    stats = {
        'users': User.query.count(),
        'facilities': Facility.query.count(),
        'reviews': Review.query.count(),
        'reports': Report.query.count(),
        'pending_reports': Report.query.filter_by(status='Pending').count(),
        'feedbacks': Feedback.query.count()
    }

    users = User.query.all()
    facilities = Facility.query.all()
    reports = Report.query.order_by(Report.created_at.desc()).all()
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

    return render_template('admin_dashboard.html',
                           stats=stats,
                           users=users,
                           facilities=facilities,
                           reports=reports,
                           feedbacks=feedbacks)


# ============ API ROUTES ============

@app.route('/api/facilities', methods=['GET'])
def api_get_facilities():
    query = request.args.get('q', '')
    city = request.args.get('city', '')
    category = request.args.get('category', '')
    wheelchair = request.args.get('wheelchair', '')

    facilities = Facility.query

    if query:
        facilities = facilities.filter(Facility.name.contains(query))
    if city:
        facilities = facilities.filter(Facility.city == city)
    if category:
        facilities = facilities.filter(Facility.category == category)
    if wheelchair == 'true':
        facilities = facilities.filter(Facility.wheelchair_accessible == True)

    results = facilities.all()

    return jsonify([{
        'id': f.id,
        'name': f.name,
        'category': f.category,
        'address': f.address,
        'city': f.city,
        'latitude': f.latitude,
        'longitude': f.longitude,
        'description': f.description,
        'wheelchair_accessible': f.wheelchair_accessible,
        'has_ramp': f.has_ramp,
        'has_accessible_toilet': f.has_accessible_toilet,
        'has_elevator': f.has_elevator,
        'has_accessible_parking': f.has_accessible_parking,
        'average_rating': f.average_rating
    } for f in results])


@app.route('/api/facility/<int:facility_id>', methods=['GET'])
def api_get_facility(facility_id):
    f = Facility.query.get_or_404(facility_id)
    return jsonify({
        'id': f.id,
        'name': f.name,
        'category': f.category,
        'address': f.address,
        'city': f.city,
        'latitude': f.latitude,
        'longitude': f.longitude,
        'description': f.description,
        'wheelchair_accessible': f.wheelchair_accessible,
        'has_ramp': f.has_ramp,
        'has_accessible_toilet': f.has_accessible_toilet,
        'has_elevator': f.has_elevator,
        'has_accessible_parking': f.has_accessible_parking,
        'average_rating': f.average_rating
    })


@app.route('/api/reviews/<int:facility_id>', methods=['GET', 'POST'])
def api_reviews(facility_id):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify({'error': 'Login required'}), 401

        data = request.get_json()
        review = Review(
            facility_id=facility_id,
            user_id=current_user.id,
            rating=int(data.get('rating', 5)),
            comment=data.get('comment', '')
        )
        db.session.add(review)
        db.session.commit()

        facility = Facility.query.get(facility_id)
        all_reviews = Review.query.filter_by(facility_id=facility_id).all()
        if all_reviews:
            facility.average_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Review added!'})

    reviews = Review.query.filter_by(facility_id=facility_id).all()
    return jsonify([{
        'id': r.id,
        'username': r.user.username,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
    } for r in reviews])


@app.route('/api/report/<int:report_id>', methods=['PUT'])
@login_required
def api_update_report(report_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    report = Report.query.get_or_404(report_id)
    report.status = data.get('status', report.status)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Report updated!'})


@app.route('/api/stats', methods=['GET'])
def api_stats():
    return jsonify({
        'facilities': Facility.query.count(),
        'reviews': Review.query.count(),
        'users': User.query.count(),
        'reports': Report.query.count()
    })


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    print("=" * 60)
    print("  ACCESSMAP - Accessibility Mapping System")
    print("=" * 60)
    print("  Server running at: http://127.0.0.1:5000")
    print("  Admin login: admin / admin123")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)