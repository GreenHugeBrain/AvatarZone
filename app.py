from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import paypalrestsdk
from forms import RegistrationForm, LoginForm
from apscheduler.schedulers.background import BackgroundScheduler
import requests  # For fetching the IP address
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'QDASFIJF89F89234FH89WHG34G89H3489GH'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# PayPal configuration
paypalrestsdk.configure({
    "mode": "live",  # sandbox or live
    "client_id": "ARS7hUnyIB3vzRyYBZwNcG7xiUmkXbKxjJZi3YzzJMBR8roMqCDJuJorGwAmT2xBPPvBhqKR9vioxGPP",
    "client_secret": "EN-dI01iEKIGx_X1TXzT5mJYGa6XX0BltMNLCmyf7ok7Pykc4qDpusLgu0GKjBvpHEtzGsIvaM21p3jv"
})

class BaseModel:
    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.commit()

class User(db.Model, UserMixin, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    basicbuyer = db.Column(db.Boolean(), nullable=False, default=False)
    standartbuyer = db.Column(db.Boolean(), nullable=False, default=False)
    premiumbuyer = db.Column(db.Boolean(), nullable=False, default=False)
    role = db.Column(db.String(50))
    ip = db.Column(db.String(150), unique=True)
    time = db.Column(db.Integer())

    def has_permission(self, permission):
        if permission == 'basic':
            return self.basicbuyer
        elif permission == 'standart':
            return self.standartbuyer
        elif permission == 'premium':
            return self.premiumbuyer
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/basic', methods=['POST'])
def basic():
    return paypal_payment('basic')

@app.route('/standart', methods=['POST'])
def standart():
    return paypal_payment('standart')

@app.route('/premium', methods=['POST'])
def premium():
    return paypal_payment('premium')

@app.route('/pay', methods=['GET', 'POST'])
def pay():
    form = RegistrationForm()
    register_success = False

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email is already registered.', 'danger')
        else:
            # Get the real IP address from the ipify API
            try:
                ip_response = requests.get('https://api.ipify.org?format=json')
                ip_response.raise_for_status()
                ip_address = ip_response.json().get('ip')
            except requests.RequestException as e:
                ip_address = 'Unknown'  # Fallback if IP retrieval fails

            hashed_password = generate_password_hash(form.password.data)
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                ip=ip_address,
                time=form.groupID.data
            )
            new_user.create()
            register_success = True
            return render_template('pay.html', form=form, RegisterSuccess=register_success)
    
    return render_template('pay.html', form=form, RegisterSuccess=register_success)

def create_paypal_payment(item_name, item_price):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": url_for('payment_execute', _external=True),
            "cancel_url": url_for('home', _external=True)},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": item_name,
                    "sku": "001",
                    "price": item_price,
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {"total": item_price, "currency": "USD"},
            "description": f"Payment for {item_name}"}]})

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return link.href
    else:
        print(payment.error)
        return None


@app.route('/download/<plan>')
@login_required
def download(plan):
    if plan not in ['basic', 'standart', 'premium']:
        abort(404)  # Return a 404 error if the plan is invalid

    # Check if the user has permission for the requested plan
    if plan == 'basic' and not current_user.has_permission('basic'):
        flash('You do not have Basic status to download this version.', 'danger')
        return redirect(url_for('home'))
    elif plan == 'standart' and not current_user.has_permission('standart'):
        flash('You do not have Standart status to download this version.', 'danger')
        return redirect(url_for('home'))
    elif plan == 'premium' and not current_user.has_permission('premium'):
        flash('You do not have Premium status to download this version.', 'danger')
        return redirect(url_for('home'))

    # Define the file path for each plan relative to the 'static' directory
    file_paths = {
        'basic': 'programs/AvatarZone.rar',  # File in static/programs
        'standart': 'files/standart_version.zip',  # File in static/files
        'premium': 'files/premium_version.zip'   # File in static/files
    }

    file_path = file_paths.get(plan)
    
    if not file_path:
        abort(404)  # Return a 404 error if the file path is not found

    # Serve the file from the static directory
    return send_from_directory(directory='static', filename=file_path)



@app.route('/paypal_payment/<plan>', methods=['POST'])
def paypal_payment(plan):
    plans = {
        'basic': ("Avatar Finder Basic", "8.00"),
        'standart': ("Avatar Finder Standart", "18.00"),
        'premium': ("Avatar Finder Premium", "150.00")
    }

    if plan in plans:
        item_name, item_price = plans[plan]
        approval_url = create_paypal_payment(item_name, item_price)
        if approval_url:
            return redirect(approval_url)
        else:
            flash('An error occurred while creating the payment.')
            return redirect(url_for('home'))
    else:
        flash('Invalid payment plan selected.')
        return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role == 'admin':
        users = User.query.all()
        return render_template('admin_panel.html', users=users)
    return redirect('/')

def decrement_user_time():
    with app.app_context():
        users = User.query.all()
        for user in users:
            if user.time is not None and user.time > 0:
                user.time -= 1
                user.save()
                if user.time == 0:
                    user.delete()

# Schedule the decrement function to run every 24 hours
scheduler.add_job(decrement_user_time, 'interval', hours=24)

@app.route('/admin_panel_update')
@login_required
def admin_panel_update():
    if current_user.role == 'admin':
        users = User.query.all()
        for user in users:
            if user.time > 0:
                user.time -= 1
                user.save()
        return render_template('admin_panel.html', users=users)
    return redirect('/')

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    user.delete()
    flash('User has been deleted successfully.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/grant_permission/<permission>/<int:user_id>', methods=['POST'])
@login_required
def grant_permission(permission, user_id):
    user = User.query.get_or_404(user_id)
    if permission == 'basic':
        user.basicbuyer = True
    elif permission == 'standart':
        user.standartbuyer = True
    elif permission == 'premium':
        user.premiumbuyer = True
    else:
        flash('Invalid permission type.', 'danger')
        return redirect(url_for('admin_panel'))
    user.save()
    flash(f'User {user.username} has been granted {permission} permissions.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/remove_all_perms/<int:user_id>', methods=['POST'])
@login_required
def remove_all_perms(user_id):
    user = User.query.get_or_404(user_id)
    user.basicbuyer = False
    user.standartbuyer = False
    user.premiumbuyer = False
    user.save()
    flash(f'All permissions have been removed from user {user.username}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/payment_execute', methods=['GET'])
def payment_execute():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        flash('Payment successful!')
        return redirect(url_for('home'))
    else:
        flash('Payment execution failed.')
        return redirect(url_for('home'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('admin_panel'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{'username': user.username, 'email': user.email, 'role': user.role, 'ip':user.ip} for user in users]
    return jsonify(users_list)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='adminuser').first():
            new_user = User(username='adminuser', email='adminuser@example.com', password='adminuser15129', role='admin')
            new_user.create()
        if not User.query.filter_by(username='normaluser').first():
            normal_user = User(username='normaluser', email='normaluser@example.com', password='normaldefaultuser', role='guest')
            normal_user.create()

    app.run(host='0.0.0.0', port=2018,debug=True)