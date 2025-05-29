import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models.user import User
from app.forms.auth_forms import RegistrationForm, LoginForm, UpdateAccountForm

auth_bp = Blueprint('auth', __name__)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('posts.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('posts.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('posts.index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('posts.index'))

@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_image = picture_file
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        try:
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('auth.account'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating account: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    image_file = url_for('static', filename='uploads/' + current_user.profile_image)
    return render_template('auth/account.html', title='Account', 
                           image_file=image_file, form=form)