
from functools import wraps
from flask import render_template, url_for, flash, redirect, request, Response
from flask.globals import session
from single_store import app, db, bcrypt
from single_store.forms import HorizontalPanelForm, EditHorizontalPanelForm, BrandForm, EditBrandForm, FeaturesForm, EditFeaturesForm, HeroForm, EditHeroForm, RegistrationForm, LoginForm, UpdateAccountForm, ProductForm, EditProductForm, CategoryForm,EditCategoryForm
from single_store.models import Attributes,HorizontalPanel, Brand, Cart, Category, Features, Hero, Order, Product, Rating, Shipping, User, MyAdminIndexView, AdminView
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os, sys
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
admin.add_view(AdminView(Hero, db.session))
admin.add_view(AdminView(Features, db.session))
admin.add_view(AdminView(HorizontalPanel, db.session))


def restricted(access_level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.role == access_level:
                return redirect(url_for('home'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.errorhandler(404)
def not_found(e):
    return render_template("single-store/404-page.djhtml")

@app.context_processor
def global_attr():
    products = Product.query.all()
    form1 = LoginForm()
    return dict(products = products, form1=form1)

@app.route("/")
def home():
    heroSlider = Hero.query.all()
    featuresService = Features.query.all()
    
    horizontalPanel = HorizontalPanel.query.get(1) # id=1 data fetch from horizontalpanel db
    
    if not heroSlider:
        heroSlider = Hero(title = "The Hero Section",
                                            description = "Write The Descriptions Here",
                                            button = "Explore More",
                                            imageFile = "default.jpg")
        heroSlider = [heroSlider]
    if horizontalPanel is None:
        horizontalPanel = HorizontalPanel(title = "The Horizontal panel ad banner",
                                            description = "Write The Descriptions Here",
                                            button = "Shop Now",
                                            imageFile = "default.jpg")
    return render_template(
        'single-store/home.djhtml', heroSlider = heroSlider, featuresService = featuresService, horizontalPanel = horizontalPanel)

@app.route("/quickview")
def quickview():
    render_template("single-store/quick-view-modal-block.html")

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

@app.route("/cart")
def cart():
    return render_template(
        'single-store/cart-page.djhtml'
        )

@app.route("/checkout")
def checkout():
    return render_template(
        'single-store/checkout-page.djhtml'
        )

@app.route("/wishlist")
def wishlist():
    return render_template(
        'single-store/wishlist-page.djhtml'
        )

@app.route("/compare")
def compare():
    return render_template(
        'single-store/compare-page.djhtml'
        )

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template(
        'single-store/admin/dashboard.djhtml'
        )

@app.route("/account", methods=['GET', 'POST'])
def user_account():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form2 = RegistrationForm()
    form1 = LoginForm()
    if request.method == 'POST':
        form_name = request.form['form-name']
        if form_name == 'form1':
            if form1.validate_on_submit():
                user = User.query.filter_by(email = form1.email.data).first()
                if user and bcrypt.check_password_hash(user.password, form1.password.data):
                    login_user(user, remember=form1.remember.data)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('user_dashboard'))
                else:
                    flash('Login Unsuccessful. Please check email and password', 'danger')

        elif form_name == 'form2':
            
            if form2.validate_on_submit():
                hashed_password = bcrypt.generate_password_hash(form2.password.data).decode('utf-8')
                user = User(userName=form2.username.data, email=form2.email.data, password=hashed_password)
                db.session.add(user)
                db.session.commit()
                flash(f'Account created for {form2.username.data}! Please Login to continue', 'success')
            else:
                flash('Failed to Cerate Account', 'danger')

    return render_template(
        'single-store/user-account/user-account.djhtml', form1=form1, form2 = form2
        )

@app.route("/dashboard")
@login_required
def user_dashboard():
    return render_template(
        'single-store/user-account/user-dashboard.djhtml'
        )

@app.route("/address-book")
def address_book():
    return render_template(
        'single-store/user-account/address-book.djhtml'
        )

@app.route("/edit-address")
def edit_address():
    return render_template(
        'single-store/user-account/edit-address.djhtml'
        )

@app.route("/edit-profile")
def edit_profile():
    return render_template(
        'single-store/user-account/edit-profile.djhtml'
        )

@app.route("/order-details")
def order_details():
    return render_template(
        'single-store/user-account/order-details.djhtml'
        )

@app.route("/order-history")
def order_history():
    return render_template(
        'single-store/user-account/order-history.djhtml'
        )

@app.route("/change-password")
def change_password():
    return render_template(
        'single-store/user-account/password.djhtml'
        )


@app.route("/about")
def about():
    return render_template('about.html', title='About')


# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user = User(userName=form.username.data, email=form.email.data, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()
#         flash(f'Account created for {form.username.data}!', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)


@app.route("/logout")
@login_required
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


# @app.route("/account", methods=['GET', 'POST'])
# @login_required
# def account():
#     form = UpdateAccountForm()
#     if form.validate_on_submit():
#         if form.picture.data:
#             random_hex = secrets.token_hex(4)
#             picture_file = save_picture(form.picture.data, random_hex + current_user.username, 'users', 700, 700)
#             current_user.image_file = picture_file
#         current_user.username = form.username.data
#         current_user.email = form.email.data
#         db.session.commit()
#         flash('Your Account has been udated!', 'success')
#         return redirect(url_for('account'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.email.data = current_user.email
#     image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
#     return render_template('account.html', title='Account', image_file=image_file, form = form)


@app.route("/add_product", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def add_product():

    product_table = Product()
    form = ProductForm()
    form.category.choices = [(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
    form.brand.choices = [(brand.name) for brand in Brand.query.with_entities(Brand.name).all()]
    if form.validate_on_submit():
        
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            featuredImage = save_picture(form.imageFile.data, random_hex + form.productName.data, 'products', 700, 700)
            
        if form.imageGallery.data:
            galleryImages = ""
            file_list = request.files.getlist('imageGallery')
            print(file_list)
            for f in file_list:
                random_hex = secrets.token_hex(4)
                file_name = f
                images = save_picture(file_name, random_hex + form.productName.data, 'gallery', 700, 700)
                galleryImages = galleryImages + "," + images

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
                            imageGallery = galleryImages,
                            tags = form.tags.data,
                            badgeDuration = form.badgeDuration.data,
                            excludeBadge = form.excludeBadge.data,
                            featured = form.featured.data,
                            product_user_id = current_user,
                            )
            db.session.add(product)
            db.session.commit()
            flash(form.productName.data+' Product Added Successful!', 'success')
        else:
            # form.productName.data = 
            # form.email.data = current_user.email
            flash('Product Edited Successful!', 'success')
            # return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_product.html', title='New Product', form=form)


@app.route("/edit_product/<int:productId>", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def edit_product(productId):
    product = Product.query.get_or_404(productId)
    form = EditProductForm()
    form.category.choices = [(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
    form.brand.choices = [(brand.name) for brand in Brand.query.with_entities(Brand.name).all()]
    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            featuredImage = save_picture(form.imageFile.data, random_hex + form.productName.data, 'products', 700, 700)
            print(featuredImage)

        if form.imageGallery.data:
            galleryImages = ""
            file_list = request.files.getlist('imageGallery')
            print(file_list)
            for f in file_list:
                random_hex = secrets.token_hex(4)
                file_name = f
                images = save_picture(file_name, random_hex + form.productName.data, 'gallery', 700, 700)
                galleryImages = galleryImages + "," + images

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
            product.imageFile = featuredImage
            product.imageGallery = galleryImages,
            product.tags = form.tags.data
            product.badgeDuration = form.badgeDuration.data
            product.excludeBadge = form.excludeBadge.data
            product.featured = form.featured.data
            product.product_user_id = current_user
            db.session.commit()
            flash(form.productName.data+' Product Updated Successful!', 'success')
    elif request.method == 'GET' :
        #db data are fetch in form in this method
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
        form.tags.data = product.tags 
        form.badgeDuration.data = product.badgeDuration
        form.excludeBadge.data = product.excludeBadge
        form.featured.data = product.featured
    return render_template('edit_product.html', title= product.productName, form=form)


@app.route("/add_category", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
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
@restricted(access_level="Admin")
def edit_category(categoryId):
    category = Category.query.get_or_404(categoryId)
    form = EditCategoryForm()
    form.parentCategory.choices = ['None']+[(category.name) for category in Category.query.with_entities(Category.name).all()]
    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            image = save_picture(form.imageFile.data, random_hex + form.name.data, 'category', 700, 700)

        if request.form.get('submit'):
            category.name = form.name.data
            category.slug = form.slug.data
            category.parentCategory = form.parentCategory.data
            category.description = form.description.data
            category.imageFile = image
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
@restricted(access_level="Admin")
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
            flash(form.name.data+' Brand Added Successful!', 'success')
        
        # return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_brand.html', title='New Brand', form=form)

@app.route("/edit_brand/<int:brandId>", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def edit_brand(brandId):

    brand = Brand.query.get_or_404(brandId)
    form = EditBrandForm()

    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            image = save_picture(form.imageFile.data,random_hex + form.name.data, 'brand', 700, 700)
        
        if request.form.get('submit'):
            brand.name = form.name.data
            brand.slug = form.slug.data
            brand.description = form.description.data
            brand.imageFile = image
            db.session.commit()
            flash(form.name.data+' Brand Updated Successful!', 'success')
    
    elif request.method == 'GET' :
        form.name.data = brand.name 
        form.slug.data = brand.slug  
        form.description.data = brand.description 
        form.imageFile.data = brand.imageFile 
    return render_template('edit_brand.html', title=brand.name, form=form)

@app.route("/add_hero", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
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
            flash(form.title.data+' Hero section Added Successful!', 'success')
        
        # return redirect(url_for('home'))

    # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('add_hero.html', title='New Hero', form=form)

@app.route("/edit_hero/<int:heroId>", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def edit_hero(heroId):

    hero=Hero.query.get_or_404(heroId)
    form = EditHeroForm()
        
    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            image = save_picture(form.imageFile.data, random_hex + form.title.data, 'hero/desktop', 840, 395)
            image = save_picture(form.imageFile.data, random_hex + form.title.data, 'hero/mobile', 510, 395)

        if request.form.get('submit'):
            hero.title = form.title.data
            hero.description = form.description.data
            hero.button = form.button.data
            hero.imageFile =image
            db.session.commit()
            flash(form.title.data+' Hero section Updated Successful!', 'success')

    elif request.method == 'GET' :
        form.title.data = hero.title 
        form.description.data = hero.description  
        form.button.data = hero.button 
        form.imageFile.data = hero.imageFile
    return render_template('edit_hero.html', title=hero.title, form=form)

@app.route("/add_feature", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
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

@app.route("/edit_feature/<int:featureId>", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def edit_feature(featureId):
    features=Features.query.get_or_404(featureId)
    form = EditFeaturesForm()
        
    if form.validate_on_submit():

        if request.form.get('submit'):
            features.title = form.title.data
            features.description = form.description.data
            features.icon = form.icon.data
            db.session.commit()
            flash(form.title.data+' Feature Added Successful!', 'success')

    elif request.method == 'GET':
        form.title.data = features.title
        form.description.data = features.description
        form.title.icon = features.icon
    return render_template('edit_feature.html', title=form.title.data, form=form)

@app.route("/add_horizontalpanel", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def add_horizontal():

    horizontal_table = HorizontalPanel()
    form = HorizontalPanelForm()
        
    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            image = save_picture(form.imageFile.data, random_hex + form.title.data, 'horizontalPanel/desktop', 1110, 170)
            image = save_picture(form.imageFile.data, random_hex + form.title.data, 'horizontalPanel/mobile', 510, 390)

        if request.form.get('submit'):
            horizontal = HorizontalPanel(title = form.title.data, 
                            description = form.description.data,
                            button = form.button.data,
                            imageFile =image,
                            )
            db.session.add(horizontal)
            db.session.commit()
            flash(form.title.data+' Horizontal Panel section Added Successful!', 'success')
    return render_template('add_horizontalPanel.html', title='New Horizontal Panel', form=form)

@app.route("/edit_horizontal/<int:horizontalId>", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def edit_horizontal(horizontalId):

    horizontal=HorizontalPanel.query.get_or_404(horizontalId)
    form = EditHorizontalPanelForm()
        
    if form.validate_on_submit():
        if form.imageFile.data:
            random_hex = secrets.token_hex(4)
            image = save_picture(form.imageFile.data, random_hex + form.title.data, 'horizontalPanel/desktop', 840, 395)
            image = save_picture(form.imageFile.data, random_hex + form.title.data, 'horizontalPanel/mobile', 510, 395)

        if request.form.get('submit'):
            horizontal.title = form.title.data
            horizontal.description = form.description.data
            horizontal.button = form.button.data
            horizontal.imageFile =image
            db.session.commit()
            flash(form.title.data+' horizontal panel Updated Successful!', 'success')

    elif request.method == 'GET' :
        form.title.data = horizontal.title 
        form.description.data = horizontal.description  
        form.button.data = horizontal.button 
        form.imageFile.data = horizontal.imageFile
    return render_template('edit_horizontalPanel.html', title=horizontal.title, form=form)

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


def str2Class(str):
    return getattr(sys.modules[__name__], str)

@app.route("/lists/<tables>")
@login_required
@restricted(access_level="Admin")
def lists(tables):
    table = str2Class(tables)

    table_col = table.__table__.columns.keys()
    table_row = table.query.all()

    if table_row is None:
        return redirect(url_for('home'))
    
    return render_template(
		'lists.html', tables = tables, table_row = table_row, table_col = table_col)

@app.route("/delete/<tables>/<int:id>")
@login_required
@restricted(access_level="Admin")
def delete(tables, id):
    table = str2Class(tables)
    table_name = tables.lower()
    if table.query.filter_by(id=id).delete():
        db.session.execute("ALTER SEQUENCE "+ table_name +"_id_seq RESTART WITH 1")
        db.session.commit()
        print("Success")
    else:
        print("Failed")
    return redirect('/lists/'+tables)
