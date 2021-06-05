from enum import unique
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.fields.core import IntegerField, RadioField, SelectField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from single_store.models import User
from wtforms import MultipleFileField

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Enter Username"})
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Re-Password"})
    submit = SubmitField('Sign Up')

    # def validate_username(self, username):
    #     user = User.query.filter_by(userName = username.data).first()
    #     if user:
    #         raise ValidationError('Username already taken. Please choose different one')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email already Registered')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
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
    imageGallery = MultipleFileField('Gallery', validators = [FileAllowed(['jpg', 'png'])])
    tags = StringField('Tags')
    badgeDuration = IntegerField('Badge Durations')
    excludeBadge = BooleanField("Exclude Badge")
    featured = BooleanField("Featured")
    # product_user_id = current_user

    submit = SubmitField('Add Product')

class EditProductForm(FlaskForm):
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
    tags = StringField('Tags')
    badgeDuration = IntegerField('Badge Durations')
    excludeBadge = BooleanField("Exclude Badge")
    featured = BooleanField("Featured")
    # product_user_id = current_user

    submit = SubmitField('Update Product')


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    parentCategory = SelectField('Parent Category', choices=[])
    description = TextAreaField('Description')
    imageFile = FileField('Category Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Category')

class EditCategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    parentCategory = SelectField('Parent Category', choices=[])
    description = TextAreaField('Description')
    imageFile = FileField('Category Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Category')


class BrandForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    description = TextAreaField('Description')
    imageFile = FileField('Brand Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Brand')

class EditBrandForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    description = TextAreaField('Description')
    imageFile = FileField('Brand Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Brand')

class HeroForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    button = StringField('Button Text')
    imageFile = FileField('Hero Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Hero Section')

class EditHeroForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    button = StringField('Button Text')
    imageFile = FileField('Hero Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Hero Section')


class FeaturesForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    icon = StringField('Icons')
    submit = SubmitField('Add Feature')

class EditFeaturesForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    icon = StringField('Icons')
    submit = SubmitField('Update Feature')

class HorizontalPanelForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    button = StringField('Button Text')
    imageFile = FileField('Horizontal Panel Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Horizontal Panel')

class EditHorizontalPanelForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    button = StringField('Button Text')
    imageFile = FileField('Horizontal Panel Image', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Horizontal Panel')


class RatingForm(FlaskForm):
    rate = RadioField('Review Stars', choices=[(1,'1 Star'),(2,'2 Stars'),(3,'3 Stars'),(4,'4 Stars'),(5,'5 Stars')], validators=[DataRequired()])
    comments = TextAreaField('Your Review')
    submit = SubmitField('Post Your Review')


class AttributesForm(FlaskForm):
    color = StringField('Add Color')
    size = StringField('Add Size')
    submit = SubmitField('Save Attributes')



class DynamicForm(FlaskForm):
    form_type = HiddenField(default='FormType', render_kw={ 'type':'hidden' })
    # name = StringField() 
