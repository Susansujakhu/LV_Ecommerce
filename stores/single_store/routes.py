
from flask import render_template, url_for, flash, redirect, request, Response
from flask.globals import session
from single_store import app, db, bcrypt
from single_store.forms import BrandForm, FeaturesForm, HeroForm, RegistrationForm, LoginForm, UpdateAccountForm, ProductForm, EditProductForm, CategoryForm,EditCategoryForm
from single_store.models import Attributes, Brand, Cart, Category, Features, Hero, Order, Product, Rating, Shipping, User, MyAdminIndexView, AdminView
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
    heroSlider = Hero.query.all()
    featuresService = Features.query.all()
    return render_template(
        'single-store/home.djhtml', heroSlider = heroSlider, featuresService = featuresService)

@app.route("/single/<int:productId>")
def single_product(productId):
    product = Product.query.get(productId)
    if product is None:
        return redirect(url_for('home'))
    
    return render_template(
		'single-store/single-product-page.djhtml', title = product.productName, product = product)
		

@app.route("/shop")
def shop():
    return render_template(
        'single-store/shop-page.djhtml'
        )

@app.route("/account")
def user_account():
    return render_template(
        'single-store/user-account.djhtml'
        )



# @app.route("/")
# def home():
#     product = Product.query.all()
#     return render_template('home.html', title = "Home", product = product)

# @app.route("/product/<int:productId>")
# def post(productId):
#     product = Product.query.get(productId)
#     if product is None:
#         return redirect(url_for('home'))
#     return render_template('single-store/single-product-page.djhtml', title = product.productName, product = product)



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

def save_picture(form_picture, name, path, width, height):
    
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = name + f_ext
    picture_path = os.path.join(app.root_path, 'static/assets/images/'+path, picture_fn)

    output_size = (width, height)
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
            random_hex = secrets.token_hex(4)
            picture_file = save_picture(form.picture.data, random_hex + current_user.username, 'users', 700, 700)
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
        
        print(form.imageFile.data)
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            featuredImage = save_picture(form.imageFile.data, random_hex + form.productName.data, 'products', 700, 700)
            print(featuredImage)
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
                            imageFile = featuredImage,
                            imageGallery = form.imageGallery.data,
                            tags = form.tags.data,
                            badgeDuration = form.badgeDuration.data,
                            excludeBadge = form.excludeBadge.data,
                            featured = form.featured.data,
                            product_user_id = current_user,
                            )
            # db.session.add(product)
            # db.session.commit()
            flash('Product Added Successful!', 'success')
        else:
            # form.productName.data = 
            # form.email.data = current_user.email
            flash('Product Edited Successful!', 'success')
            # return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_product.html', title='New Product', form=form)


@app.route("/edit_product/<int:productId>", methods=['GET', 'POST'])
@login_required
def edit_product(productId):
    product = Product.query.get_or_404(productId)
    form = EditProductForm()
    form.category.choices = [(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
    form.brand.choices = [(brand.name) for brand in Brand.query.with_entities(Brand.name).all()]
    if form.validate_on_submit():
        if form.imageFile.data:
            featuredImage = save_picture(form.imageFile.data)

        if form.imageGallery.data:
            galleryImage = save_picture(form.imageGallery.data)

        if request.form.get('submit'):
            product.productName = form.productName.data
            product.slug = form.slug.data
            product.price = form.price.data
            product.discount = form.discount.data
            product.stock = form.stock.data
            product.category = form.category.data
            product.brand = form.brand.data
            product.color = form.color.data
            product.size = form.size.data
            product.weight = form.weight.data
            product.dimension = form.dimension.data
            product.material = form.material.data
            product.shortDescription = form.shortDescription.data
            product.longDescription = form.longDescription.data
            # product.imageFile = form.imageFile.data
            # product.imageGallery = form.imageGallery.data
            product.featured = form.featured.data
            product.product_user_id = current_user
            db.session.commit()
            flash(form.productName.data+' Product Updated Successful!', 'success')
    elif request.method == 'GET' :
        form.productName.data = product.productName 
        form.slug.data = product.slug 
        form.price.data = product.price
        form.discount.data = product.discount
        form.stock.data = product.stock
        form.category.data = product.category
        form.brand.data = product.brand
        form.color.data = product.color
        form.size.data  = product.size
        form.weight.data = product.weight 
        form.dimension.data = product.dimension 
        form.material.data = product.material 
        form.shortDescription.data = product.shortDescription 
        form.longDescription.data = product.longDescription
        form.imageFile.data = product.imageFile
        form.imageGallery.data = product.imageGallery
        form.featured.data = product.featured 
    return render_template('edit_product.html', title= product.productName, form=form)


@app.route("/add_category", methods=['GET', 'POST'])
@login_required
def add_category():

    category_table = Category()
    form = CategoryForm()
    form.parentCategory.choices = ['None']+[(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
    
    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            image = save_picture(form.imageFile.data, random_hex + form.name.data, 'category', 700, 700)

        if request.form.get('submit'):
            category = Category(name = form.name.data, 
                            slug = form.slug.data,
                            parentCategory = form.parentCategory.data,
                            description = form.description.data,
                            imageFile = image,
                            )
            db.session.add(category)
            db.session.commit()
            flash('Category Added Successful!', 'success')
        
        # return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_category.html', title='New Category', form=form)



@app.route("/edit_category/<int:categoryId>", methods=['GET', 'POST'])
@login_required
def edit_category(categoryId):
    category = Category.query.get_or_404(categoryId)
    form = EditCategoryForm()
    form.parentCategory.choices = ['None']+[(category.name) for category in Category.query.with_entities(Category.name).all()]
    if form.validate_on_submit():
        if form.imageFile.data:
            image = save_picture(form.imageFile.data)

        if request.form.get('submit'):
            category.name = form.name.data
            category.slug = form.slug.data
            category.parentCategory = form.parentCategory.data
            category.description = form.description.data
            db.session.commit()
            flash(form.name.data+' Category Updated Successful!', 'success')
    elif request.method == 'GET' :
        form.name.data = category.name 
        form.slug.data = category.slug
        form.parentCategory.data = category.parentCategory
        form.description.data = category.description
        form.imageFile.data = category.imageFile                      
    return render_template('edit_category.html', title=category.name, form=form)



@app.route("/add_brand", methods=['GET', 'POST'])
@login_required
def add_brand():

    brand_table = Brand()
    form = BrandForm()
        
    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            image = save_picture(form.imageFile.data,random_hex + form.name.data, 'brand', 700, 700)

        if request.form.get('submit'):
            brand = Brand(name = form.name.data, 
                            slug = form.slug.data,
                            description = form.description.data,
                            imageFile = image,
                            )
            db.session.add(brand)
            db.session.commit()
            flash('Brand Added Successful!', 'success')
        
        # return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_brand.html', title='New Brand', form=form)

@app.route("/add_hero", methods=['GET', 'POST'])
@login_required
def add_hero():

    hero_table = Hero()
    form = HeroForm()
        
    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            image = save_picture(form.imageFile.data, random_hex + form.title.data, 'hero/desktop', 840, 395)
            image = save_picture(form.imageFile.data, random_hex + form.title.data, 'hero/mobile', 510, 395)

        if request.form.get('submit'):
            hero = Hero(title = form.title.data, 
                            description = form.description.data,
                            button = form.button.data,
                            imageFile =image,
                            )
            db.session.add(hero)
            db.session.commit()
            flash('Hero Added Successful!', 'success')
        
        # return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_hero.html', title='New Hero', form=form)

@app.route("/add_feature", methods=['GET', 'POST'])
@login_required
def add_feature():

    features_table = Features()
    form = FeaturesForm()
        
    if form.validate_on_submit():

        if request.form.get('submit'):
            feature = Features(title = form.title.data, 
                            description = form.description.data,
                            icon = form.icon.data,
                            )
            db.session.add(feature)
            db.session.commit()
            flash('Feature Added Successful!', 'success')
        
        # return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_feature.html', title='New Feature', form=form)



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


