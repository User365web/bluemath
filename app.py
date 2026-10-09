import os
import secrets
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import (
    Flask, Response, abort, flash, jsonify, redirect, render_template,
    request, session, url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('COOKIE_SECURE', 'false').lower() == 'true'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# Use a managed PostgreSQL database in production. SQLite is a convenient local fallback.
database_url = os.environ.get('DATABASE_URL', '').strip()
if database_url.startswith('postgres://'):
    database_url = 'postgresql+psycopg://' + database_url[len('postgres://'):]
elif database_url.startswith('postgresql://'):
    database_url = 'postgresql+psycopg://' + database_url[len('postgresql://'):]
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    instance_dir = Path(app.instance_path)
    instance_dir.mkdir(parents=True, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + (instance_dir / 'bluemath.db').as_posix()

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
db = SQLAlchemy(app)


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, nullable=False, default=False)


with app.app_context():
    db.create_all()


def csrf_token():
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return token


app.jinja_env.globals['csrf_token'] = csrf_token


def verify_csrf():
    supplied = request.form.get('_csrf_token', '')
    expected = session.get('_csrf_token', '')
    if not supplied or not expected or not secrets.compare_digest(supplied, expected):
        abort(400, description='Invalid form token. Please reload the page and try again.')


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.get('/robots.txt')
def robots_txt():
    base = request.url_root.rstrip('/')
    content = f"User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /admin/\n\nSitemap: {base}/sitemap.xml\n"
    return Response(content, mimetype='text/plain')


@app.get('/sitemap.xml')
def sitemap():
    base = request.url_root.rstrip('/')
    paths = [
        '/', '/faq', '/guides',
        '/guides/scientific-calculator-guide',
        '/guides/percentages-and-ratios',
        '/guides/quadratic-equations', '/contact', '/privacy', '/terms',
    ]
    xml_urls = ''.join(f'<url><loc>{base}{path}</loc></url>' for path in paths)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + xml_urls + '</urlset>\n'
    return Response(xml, mimetype='application/xml')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/guides')
def guides():
    return render_template('guides.html')


@app.route('/guides/<slug>')
def guide(slug):
    guides_map = {
        'scientific-calculator-guide': ('How to Use a Scientific Calculator Effectively', 'scientific-calculator-guide.html'),
        'percentages-and-ratios': ('Percentages, Ratios & Proportions: A Practical Guide', 'percentages-and-ratios.html'),
        'quadratic-equations': ('How to Solve Quadratic Equations', 'quadratic-equations.html'),
    }
    item = guides_map.get(slug)
    if not item:
        return render_template('404.html'), 404
    return render_template(item[1], title=item[0])


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.post('/api/contact')
def contact_api():
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip()
    message = str(data.get('message', '')).strip()
    if not name or not email or not message:
        return jsonify({'ok': False, 'message': 'Please complete all fields.'}), 400
    if len(name) > 120 or len(email) > 254 or len(message) > 10000:
        return jsonify({'ok': False, 'message': 'Please shorten your message and try again.'}), 400
    if '@' not in email or email.startswith('@') or email.endswith('@'):
        return jsonify({'ok': False, 'message': 'Please enter a valid email address.'}), 400
    try:
        db.session.add(ContactMessage(name=name, email=email, message=message))
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception('Failed to save contact message')
        return jsonify({'ok': False, 'message': 'We could not save your message right now. Please try again later.'}), 500
    return jsonify({'ok': True, 'message': 'Thank you! Your message has been saved. We appreciate your feedback.'})


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    configured = bool(os.environ.get('ADMIN_USERNAME') and os.environ.get('ADMIN_PASSWORD'))
    if request.method == 'POST':
        verify_csrf()
        if not configured:
            flash('Admin access is not configured yet. Set ADMIN_USERNAME and ADMIN_PASSWORD in your hosting environment.', 'error')
        else:
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            correct_user = secrets.compare_digest(username, os.environ['ADMIN_USERNAME'])
            correct_pass = secrets.compare_digest(password, os.environ['ADMIN_PASSWORD'])
            if correct_user and correct_pass:
                session.clear()
                session['is_admin'] = True
                session['admin_username'] = username
                csrf_token()
                return redirect(url_for('admin_dashboard'))
            flash('Incorrect username or password.', 'error')
    return render_template('admin_login.html', configured=configured)


@app.post('/admin/logout')
@admin_required
def admin_logout():
    verify_csrf()
    session.clear()
    flash('You have been signed out.', 'success')
    return redirect(url_for('admin_login'))


@app.get('/admin')
@admin_required
def admin_dashboard():
    view = request.args.get('view', 'all')
    query = ContactMessage.query
    if view == 'unread':
        query = query.filter_by(is_read=False)
    messages = query.order_by(desc(ContactMessage.created_at), desc(ContactMessage.id)).limit(200).all()
    unread_count = ContactMessage.query.filter_by(is_read=False).count()
    total_count = ContactMessage.query.count()
    return render_template('admin_dashboard.html', messages=messages, view=view, unread_count=unread_count, total_count=total_count)


@app.post('/admin/messages/<int:message_id>/read')
@admin_required
def admin_mark_read(message_id):
    verify_csrf()
    item = db.session.get(ContactMessage, message_id)
    if item is None:
        abort(404)
    item.is_read = not item.is_read
    db.session.commit()
    flash('Message status updated.', 'success')
    return redirect(url_for('admin_dashboard', view=request.form.get('view', 'all')))


@app.post('/admin/messages/<int:message_id>/delete')
@admin_required
def admin_delete_message(message_id):
    verify_csrf()
    item = db.session.get(ContactMessage, message_id)
    if item is None:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin_dashboard', view=request.form.get('view', 'all')))


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
