from flask import Flask,abort, session, render_template, url_for, flash, redirect, request,send_file
from portal import app, db, bcrypt,mail
from portal.forms import RegistrationForm, LoginForm,PostForm,RequestResetForm,ResetPasswordForm,UpdateAccountForm,CreateJobOfferForm
from portal.models import User, Post,jobs,company
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import os 
import json
import secrets
from os import path
from os.path import join, dirname, realpath
from sqlalchemy.sql.functions import func
from sqlalchemy.sql import text
from sqlalchemy import update
import pandas as pd
import sqlite3
from datetime import datetime ,date ,timedelta
from flask_socketio import SocketIO,send,emit
from portal import socketio

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()




@app.route("/")
def root():
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('checkUser'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('checkUser'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/checkUser")
@login_required
def checkUser():
    if current_user.is_active == True:
        return redirect(url_for('dashboard'))
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))





@app.route("/register", methods=['GET', 'POST'])
def register():
    user=User.query.all()
    checkAdmin=1
    for u in user:
        if u.is_admin==True:
            checkAdmin=0
            break
    if current_user.is_authenticated:
        return redirect(url_for('check'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.username.data=='test':
            flash('This username cannot be taken','danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password,is_active=True)
            db.session.add(user)
            db.session.commit()
            flash('Wait for admin approval', 'info')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form,check=checkAdmin)





@app.route("/admin_register/<key>", methods=['GET', 'POST'])
def admin_register(key):
    if '1800' == key:
        user=User.query.all()
        check=1
        for u in user:
            if u.is_admin==True:
                check=0
                break
        if check==1:
            if current_user.is_authenticated:
                return redirect(url_for('checkUser'))
            form = RegistrationForm()
            if form.validate_on_submit():
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(username=form.username.data, email=form.email.data, password=hashed_password,is_admin=True,is_active=True,is_candidate=True)
                db.session.add(user)
                db.session.commit()
                flash('You are now admin.', 'info')
                return redirect(url_for('login'))
            return render_template('register.html', title='Register', form=form)
        elif check==0:
            flash('Admin account already exists','info')
            return redirect(url_for('login'))
    else:
        render_template('error.html',error=404)






@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_active == True:
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        return render_template('dashboard.html',title='Dashboard',image_file=image_file)
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))


@app.route("/browse_companies")
@login_required
def browse_companies():
    if current_user.is_active == True:
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        return render_template('dashboard.html',title='Dashboard',image_file=image_file)
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))


@app.route("/create_job", methods=['GET', 'POST'])
@login_required
def create_job():
    if current_user.is_active == True:
        form=CreateJobOfferForm()
        if form.validate_on_submit():
            offer = jobs(job_title=form.job_title.data, job_type=form.job_type.data,
                job_category=form.job_category.data,location=form.location.data,
                job_description=form.job_description.data,deadline= form.deadline.data,
                min_salary=form.min_salary.data,max_salary=form.max_salary.data,
                tags=form.tags.data ,employer_id=current_user)
            db.session.add(offer)
            db.session.commit()
            return redirect(url_for('dashboard'))
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        return render_template('create_job.html',title='Create Job Offer',image_file=image_file,form=form)
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))




def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path= os.path.join(app.root_path,'static/profile_pics',picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.is_active == True:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file=picture_file
            current_user.username=form.username.data
            current_user.email=form.email.data
            current_user.firstname=form.firstname.data
            current_user.lastname=form.lastname.data
            current_user.country=form.country.data
            current_user.designation=form.designation.data
            db.session.commit()
            flash('Your account has been updaed','success')
            return redirect('profile')
        elif request.method == 'GET':
            form.username.data=current_user.username
            form.email.data=current_user.email
            form.firstname.data=current_user.firstname
            form.lastname.data=current_user.lastname
            form.country.data=current_user.country
            form.designation.data=current_user.designation
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        return render_template('profile.html', title='Profile',image_file=image_file,form=form)
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))




@app.route("/follow/<username>")
@login_required
def follow(username):
    if current_user.is_active == True:
        user_to_follow=User.query.filter_by(username=username).first()
        current_user.following.append(user_to_follow)
        db.session.commit()
        flash(username +' successfully followed ','success')
        return redirect(url_for('user',username=username))
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))



@app.route("/search")
@login_required
def search():
    if current_user.is_active == True:
        user=User.query.all()
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        return render_template('search.html', title='Search',image_file=image_file,user=user)
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))






@app.route("/people")
@login_required
def people():
    if current_user.is_active == True:
        user=User.query.all()
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        return render_template('people.html',image_file=image_file,user=user,title='Members')
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))


@app.route("/resume")
@login_required
def resume():
    if current_user.is_active == True:
        user=User.query.all()
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        return render_template('resume.html',image_file=image_file,user=user,title='Build Resume')
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))


@socketio.on('annoucement')
def annouce(msg):
    print(msg)
    emit('message','An annoucement has been made',broadcast=True)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.is_active == True:
        form=PostForm()
        user=User.query.all()
        post=Post.query.all()
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        if form.validate_on_submit():
            if current_user.is_admin==True or current_user.is_candidate==True:
                post = Post(title=form.title.data, content=form.content.data, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('new_post'))
        return render_template('announcements.html',image_file=image_file,user=user,title='Announcements',form=form,post=post)
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))

@app.route("/delete_post/<post_id>", methods=['POST','GET'])
@login_required
def delete_post(post_id):
    if current_user.is_active == True:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            return render_template('error.html',error=403)
        else:
            db.session.delete(post)
            db.session.commit()
            flash('Your post has been deleted!', 'success')
            return redirect(url_for('new_post'))

@app.route('/user/<username>')
@login_required
def user(username):
    if current_user.is_active == True:
        user = User.query.filter_by(username=username).first_or_404()
        followed_by=user.followed_by.all()
        return render_template('user.html', user=user,title='Users',followed=followed_by)
    else:
        flash('Your account has been deactivated by administrator','danger')
        return redirect(url_for('logout'))



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='flaskbeta@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(message=msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('A email has been sent with instructions to reset your password','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title= 'Reset Password',form=form)



@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


