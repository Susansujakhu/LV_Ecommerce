from enum import unique
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.fields.core import IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from single_store.models import User

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
        user = User.query.filter_by(userName = username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose different one')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email already Registered')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    picture = FileField('Update profile picture', validators = [FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.userName:
            user = User.query.filter_by(userName=username.data).first()
            if user:
                raise ValidationError('Username already taken. Please choose different one')

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('Email already Registered')



class ProductForm(FlaskForm):
    productName = StringField('Product Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    discount = IntegerField('Discount')
    stock = IntegerField('Stock', validators=[DataRequired()])
    category = SelectField('Category', choices=[] ,validators=[DataRequired()])
    brand = SelectField('Brand', choices=[])
    color = StringField('Color')
    size = StringField('Size')
    weight = StringField('Weight')
    dimension = StringField('Dimension')
    material = StringField('Material')
    shortDescription = TextAreaField('Short Description')
    longDescription = TextAreaField('Long Description')
    imageFile = FileField('Set Featured image', validators = [FileAllowed(['jpg', 'png'])])
    imageGallery = FileField('Gallery', validators = [FileAllowed(['jpg', 'png'])])
    featured = BooleanField("Featured")
    # product_user_id = current_user

    submit = SubmitField('Add Product')

    edit = SubmitField('Save Changes')


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    parentCategory = SelectField('Parent Category', choices=[])
    description = TextAreaField('Discription')
    imageFile = FileField('Category Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Category')


class BrandForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    description = TextAreaField('Discription')
    imageFile = FileField('Brand Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Brand')

class HeroForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Discription')
    button = StringField('Button Text')
    imageFile = FileField('Hero Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Hero Section')


class FeaturesForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Discription')
    icon = FileField('Features Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Feature')


