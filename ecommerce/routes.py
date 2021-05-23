
from flask import render_template, url_for, flash, redirect, request, Response
from flask.globals import session
from ecommerce import app, db, bcrypt
from ecommerce.forms import RegistrationForm, LoginForm, UpdateAccountForm, ProductForm
from ecommerce.models import Attributes, Brand, Cart, Category, Order, Product, Rating, Shipping, User, MyAdminIndexView, AdminView
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os
from PIL import Image
from flask_admin import Admin


admin = Admin(app, name='Dashboard', index_view = MyAdminIndexView())
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Shipping, db.session))
admin.add_view(AdminView(Product, db.session))
admin.add_view(AdminView(Cart, db.session))
admin.add_view(AdminView(Order, db.session))
admin.add_view(AdminView(Rating, db.session))
admin.add_view(AdminView(Attributes, db.session))
admin.add_view(AdminView(Category, db.session))
admin.add_view(AdminView(Brand, db.session))





@app.route("/")
def home():
    product = Product.query.all()
    return render_template('home.html', title = "Home", product = product)

@app.route("/product/<int:productId>")
def post(productId):
    product = Product.query.get(productId)
    if product is None:
        return redirect(url_for('home'))
    return render_template('single_product_page.html', title = product.productName, product = product)



@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(userName=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been udated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form = form)



@app.route("/add_product", methods=['GET', 'POST'])
@login_required
def add_product():

    product_table = Product()
    form = ProductForm()
    form.category.choices = [(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
    form.brand.choices = [(brand.name) for brand in Brand.query.with_entities(Brand.name).all()]
    if form.validate_on_submit():
        if form.imageFile.data:
            featuredImage = save_picture(form.imageFile.data)

        if form.imageGallery.data:
            galleryImage = save_picture(form.imageGallery.data)

        if request.form.get('submit'):
            product = Product(productName = form.productName.data, 
                            slug = form.slug.data,
                            price=form.price.data, 
                            discount=form.discount.data,
                            stock = form.stock.data,
                            category = form.category.data,
                            brand = form.brand.data,
                            color = form.color.data,
                            size = form.size.data,
                            weight = form.weight.data,
                            dimension = form.dimension.data,
                            material = form.material.data,
                            shortDescription = form.shortDescription.data,
                            longDescription = form.longDescription.data,
                            imageFile = form.imageFile.data,
                            imageGallery = form.imageGallery.data,
                            featured = form.featured.data,
                            product_user_id = current_user
                            )
            db.session.add(product)
            db.session.commit()
            flash('Product Added Successful!', 'success')
        else:
            # form.productName.data = 
            # form.email.data = current_user.email
            flash('Product Edited Successful!', 'success')
        return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_product.html', title='New Product', form=form)


# @app.route("/post/new", methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = ProductForm()
#     if form.validate_on_submit():
#         post = User(title = form.title.data, content = form.content.data, author = current_user)
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created!', 'success')
#         return redirect(url_for('home'))
#     return render_template('create_post.html', title='New Post', form = form)

# @app.route("/post/<int:post_id>")
# def post(post_id):
#     post = User.query.get_or_404(post_id)
#     return render_template('post.html', title = post.title, post =post)


