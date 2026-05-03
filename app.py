import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    requests = db.relationship('UserRequest', backref='user', lazy=True)


class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(200))
    status = db.Column(db.String(50), default='новый')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def send_email(subject, recipient, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastral')
def cadastral():
    services = [
        {'id': 1, 'title': 'Межевание земельных участков', 'description': 'Определение границ земельного участка'},
        {'id': 2, 'title': 'Кадастровая съемка', 'description': 'Полевые измерения и съемка'},
        {'id': 3, 'title': 'Постановка на кадастровый учет', 'description': 'Регистрация объектов недвижимости'},
        {'id': 4, 'title': 'Технический план', 'description': 'Подготовка технического плана здания'},
        {'id': 5, 'title': 'Акт обследования', 'description': 'Документ о прекращении существования объекта'},
        {'id': 6, 'title': 'Кадастровые консультации', 'description': 'Профессиональные консультации'},
    ]
    return render_template('cadastral.html', services=services)


@app.route('/project')
def project():
    services = [
        {'id': 1, 'title': 'Архитектурное проектирование', 'description': 'Разработка архитектурных решений'},
        {'id': 2, 'title': 'Конструктивные решения', 'description': 'Расчет и проектирование конструкций'},
        {'id': 3, 'title': 'Инженерные системы', 'description': 'Проектирование инженерных коммуникаций'},
        {'id': 4, 'title': 'Дизайн интерьера', 'description': 'Разработка дизайн-проектов'},
        {'id': 5, 'title': 'Сметная документация', 'description': 'Составление сметной документации'},
        {'id': 6, 'title': 'Авторский надзор', 'description': 'Контроль за реализацией проекта'},
    ]
    return render_template('project.html', services=services)


@app.route('/send_request', methods=['POST'])
def send_request():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    message = request.form.get('message')
    service_type = request.form.get('service_type', 'общий запрос')

    if not all([name, phone, email, message]):
        flash('Пожалуйста, заполните все обязательные поля', 'danger')
        return redirect(request.referrer)

    body = f"""
    Новая заявка с сайта:

    Имя: {name}
    Телефон: {phone}
    Email: {email}
    Тип услуги: {service_type}
    Сообщение: {message}

    Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """

    subject = f'Новая заявка: {service_type}'
    recipient = 'company@example.com'

    print("=" * 50)
    print("НОВАЯ ЗАЯВКА:")
    print(body)
    print("=" * 50)

    flash('Заявка отправлена успешно! Мы свяжемся с вами в ближайшее время.', 'success')
    return redirect(request.referrer)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже существует', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'danger')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_requests = UserRequest.query.filter_by(user_id=current_user.id).order_by(UserRequest.created_at.desc()).all()
    return render_template('dashboard.html', requests=user_requests)


@app.route('/new_request', methods=['GET', 'POST'])
@login_required
def new_request():
    if request.method == 'POST':
        service_type = request.form['service_type']
        description = request.form['description']

        if not description:
            flash('Пожалуйста, добавьте описание', 'danger')
            return redirect(url_for('new_request'))

        filename = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                filename = secure_filename(
                    f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        request_obj = UserRequest(
            user_id=current_user.id,
            service_type=service_type,
            description=description,
            filename=filename
        )

        db.session.add(request_obj)
        db.session.commit()

        flash('Заявка успешно создана!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('request_form.html')


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
