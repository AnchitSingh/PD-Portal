from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField,IntegerField,DateField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from portal.models import User
from flask_wtf.file import FileField, FileAllowed, FileRequired


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')



class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=40)])
    firstname = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=40)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=40)])
    country = StringField('Country',
                           validators=[Length(min=2, max=40)])
    designation = StringField('Designation',validators=[Length(min=2, max=40)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Picture',validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')




class FindCandidateForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')



class CreateJobOfferForm(FlaskForm):
    job_title = StringField('Title',validators=[DataRequired()])
    job_type = SelectField('Type',choices=[('Full Time', 'Full Time'), ('Freelance', 'Freelance'), ('Internship', 'Internship'), ('Part Time', 'Part Time'), ('Temporary', 'Temporary')],validators=[DataRequired()])
    job_category = SelectField('Category',choices=[('Coding', 'Coding'), ('Accounting', 'Accounting'),('Counseling', 'Counseling'), ('Web Development', 'Web Development'), ('Data Science', 'Data Science')],validators=[DataRequired()])
    location = StringField('Location',validators=[DataRequired()])
    tags = StringField('Tags',validators=[DataRequired()])
    job_description = TextAreaField('Description',validators=[DataRequired()])
    min_salary = IntegerField('Min Salary',validators=[DataRequired()])
    max_salary = IntegerField('Max Salary',validators=[DataRequired()])
    deadline = DateField('Deadline',validators=[DataRequired()])
    submit = SubmitField('Create Offer')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=TextAreaField('Content',validators=[DataRequired()])
    submit=SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first')



class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
