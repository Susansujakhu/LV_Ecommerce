from functools import wraps
from flask import render_template, url_for, flash, redirect, request, Response, jsonify
from flask.globals import session
from flask.helpers import make_response
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import text
from wtforms.fields.core import StringField
from single_store import app, db, bcrypt, mail, Message
from single_store.forms import DashboardPwForm, EditDashboardAddressForm, EditDashboardProfileForm,DynamicForm, ForgetPassword, HorizontalPanelForm, EditHorizontalPanelForm, BrandForm, EditBrandForm, FeaturesForm, EditFeaturesForm, HeroForm, EditHeroForm, RatingForm, RegistrationForm, LoginForm, ProductForm, EditProductForm, CategoryForm,EditCategoryForm, ColorForm, SizeForm
from single_store.models import Size, Color, Compare,HorizontalPanel, Brand, Cart, Category, Features, Hero, Order, Product, Rating, Shipping, User, MyAdminIndexView, AdminView, Wishlist
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os, sys
from PIL import Image
from flask_admin import Admin
from werkzeug.utils import secure_filename, validate_arguments
from datetime import datetime, timezone, timedelta 
from sqlalchemy.sql import table, column
from sqlalchemy import func
from sqlalchemy import exc
from currency_converter import CurrencyConverter

admin = Admin(app, name='Dashboard', index_view = MyAdminIndexView())
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Shipping, db.session))
admin.add_view(AdminView(Product, db.session))
admin.add_view(AdminView(Cart, db.session))
admin.add_view(AdminView(Order, db.session))
admin.add_view(AdminView(Rating, db.session))
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
    currency = request.cookies.get('currency')
    if currency is None:
        currency = "NPR"
    totalCart         = 0
    cartProductNumber = 0
    badgeForNew       = []
    form1             = LoginForm()
    products          = Product.query.all()
    category          = Category.query.all()

    productRatings = {}
    for productItem in products:
        rating        = Rating.query.filter_by(product_id = productItem.id).all()
        sum           = 0
        avg_rating    = 0
        total_ratings = len(rating)
        for rate in rating:
            sum = sum+rate.rate
        if total_ratings != 0:
            avg_rating = int(sum/total_ratings)
        productRatings[productItem.id] = [total_ratings, avg_rating]

    if current_user.is_authenticated:
        indicators = Wishlist.query.filter_by(userId = current_user.userId).first()
        if indicators is None:
            print("No Value")
            wishlist_indicator = 0
        else:
            list_product = indicators.product_list.split(",")
            if list_product[0] == '':
                wishlist_indicator = 0
            else:
                wishlist_indicator = len(list_product)
        cart = Cart.query.filter_by(userId = current_user.userId).all()
        if cart is None:
            print("No Cart Data")
        else:
            for cart_row in cart:
                for rows in products:
                    if cart_row.product_id == rows.id:
                        totalCart = (cart_row.quantity*rows.price)+totalCart
                        cartProductNumber=cartProductNumber+1
        for rows in products:
            subDate=(rows.dateCreated+timedelta(rows.badgeDuration))-datetime.today()
            if (subDate.days)>=0:
                badgeForNew.append(rows.id)
    else:
        cart = Cart.query.filter_by(userId = 1233).all()
        wishlist_indicator = 0
    return dict(products = products, form1=form1, cart=cart, totalCart=totalCart, 
                cartProductNumber=cartProductNumber, wishlist_indicator=wishlist_indicator, 
                badgeForNew = badgeForNew, currency=currency, category=category, productRatings=productRatings)

@app.context_processor
def utility_processor():
    def format_price(amount, currency='Rs. '):
        currency = request.cookies.get('currency')
        if currency is None:
            currency = "NPR"
        if currency != "NPR":
            amount = amount / 1.6
            c = CurrencyConverter()
            amount = c.convert(amount, 'INR', currency)
            amount = "{:,.2f}".format(amount)
        else:
            amount_list = [int(d) for d in str(amount)]
            amount_list.reverse()
            list_length = len(amount_list)
            for i in range(1, int(list_length/2)):
                amount_list.insert(3*i,",")

            amount_list.reverse()
            amount = ''.join([str(elem) for elem in amount_list])
            amount = amount+".00"

        return '{1} {0}'.format(amount, currency)

    return dict(format_price=format_price)


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


@app.route("/product/<slug>")
def single_product(slug):
    product = Product.query.filter_by(slug = slug).first()
    rating = Rating.query.filter_by(product_id = product.id).all()
    colors = Color.query.all()
    users = User.query.all()
    sum = 0
    avg_rating = 0
    total_ratings = len(rating)
    for rate in rating:
        sum = sum+rate.rate
    if total_ratings != 0:
        avg_rating = int(sum/total_ratings)
        
    form = RatingForm()
    if product is None:
        return redirect(url_for('home'))
    
    return render_template(
        'single-store/single-product-page.djhtml', title = product.productName, 
                product = product, form=form, rating=rating, users=users, 
                avg_rating=avg_rating, total_ratings=total_ratings, colors=colors)


@app.route("/saveReview", methods=["POST"])
@login_required
def saveReview():
    if request.method == "POST":
        rate = request.form.get("radio_val")
        comments = request.form.get("comments")
        productId = request.form.get("productId")
        # productId= int(request.get_data())
        product = Product.query.get(productId)
        form = RatingForm()

        if rate is None:
            print("Please choose at least 1 Star")
        else:
            if form.validate_on_submit:
                rate = Rating(
                            rate = rate,
                            comments = comments,
                            rating_user_id = current_user,
                            rating_product_id=product,
                            )

                db.session.add(rate)
                db.session.commit()
                print("Success Addding Review")
    return jsonify({'result': 'success'})


@app.route("/category/<slug>")
def categoryPage(slug):
    max = db.session.query(func.max(Product.price)).scalar()
    min = db.session.query(func.min(Product.price)).scalar()
    brand = Brand.query.all()
    color = Color.query.all()
    category = Category.query.filter_by(slug = slug).first()
    selectedProducts = Product.query.filter(Product.category == category.name).all()
    total_products = len(selectedProducts)
    product_number = []
    for items in brand:
        product_number.append(Product.query.filter(Product.brand == items.name).count())

    return render_template(
        'single-store/products-archive-page.djhtml', 
        max=max, min =min, brand=brand, product_number=product_number, color=color,
        total_products = total_products, show_products = 3
        )

@app.route("/search-results", methods=['GET', 'POST'])
def searchPage():

    cata = request.form.get('categories')
    keyword = request.form.get('search')

    max = db.session.query(func.max(Product.price)).scalar()
    min = db.session.query(func.min(Product.price)).scalar()
    brand = Brand.query.all()
    color = Color.query.all()

    selectedProducts = Product.query.filter(Product.category == cata).all()
    total_products = len(selectedProducts)
    product_number = []
    for items in brand:
        product_number.append(Product.query.filter(Product.brand == items.name).count())

    return render_template(
        'single-store/products-archive-page.djhtml', 
        max=max, min =min, brand=brand, product_number=product_number, color=color,
        total_products = total_products, show_products = 3, cata=cata, keyword=keyword
        )


@app.route("/shop")
def shop():
    max = db.session.query(func.max(Product.price)).scalar()
    min = db.session.query(func.min(Product.price)).scalar()
    brand = Brand.query.all()
    color = Color.query.all()
    
    total_products = Product.query.count()
    product_number = []
    for items in brand:
        product_number.append(Product.query.filter(Product.brand == items.name).count())

    return render_template(
        'single-store/products-archive-page.djhtml', 
        max=max, min =min, brand=brand, product_number=product_number, color=color,
        total_products = total_products, show_products = 3
        )

@app.route("/shopFilter", methods=["POST"])
def shopFilter():
    if request.method == "POST":
        colors           = request.form.getlist("color[]")
        brands           = request.form.getlist("brands[]")
        min              = int(float(request.form.get("min")))
        max              = int(float(request.form.get("max")))
        selectedCategory = request.form.get("category")
        sort             = request.form.get("sort")
        limit            = int(request.form.get("limit"))
        keyword          = request.form.get("keyword")
        filters          = []

        if keyword:
            filters.append(
                Product.productName.ilike('%'+keyword+'%')
            )

        if selectedCategory:
            final_category = []
            if selectedCategory.islower():
                category = Category.query.filter_by(slug = selectedCategory).first()
                selectedCategory = category.name
            final_category.append(selectedCategory)
            all_category = Category.query.all()
            for items in all_category:
                if items.parentCategory == selectedCategory:
                    final_category.append(items.name)
            print(final_category)
            filters.append(
                Product.category.in_(final_category)
            )
        
        if brands:
            print(brands)
            filters.append(
                Product.brand.in_(brands)
            )
        if colors:
            filters.append(
                Product.color.in_(colors)   
            )
        products = db.session.query(Product).filter(Product.price>=min, Product.price<=max, *filters)
        filterBrand = []
        filterColor = []
        for productRows in products:
            filterBrand.append(productRows.brand)
            
        for productRows in db.session.query(Product.color).distinct():
            filterColor.append(productRows.color)

        if sort:
            products = products.order_by(Product.productName)
        productCount = products.count()
        max_data = "False"
        if limit > productCount and productCount != 0:
            print("limit Crossed")
            limit = productCount
            max_data = "True"
        elif productCount == 0:
            max_data = "no_data"
        
        products = products[:limit]
        
        # price_list = []
        # for items in products:
        #     price_list.append(format_price(items.price))
        # print(price_list)
    return jsonify({'htmlresponse':render_template('general/blocks/response.djhtml', products=products), 
                    'limit':limit, 'max_data':max_data, 
                    'filterColor':filterColor, 
                    'filterBrand':filterBrand,

                })


@app.route("/cart", methods=["POST","GET"])
@login_required
def cart():
    message = "Your cart is empty"
    if request.method == "POST":    #to increase/decrease the quantity of cart 
        quantityNum = request.form['quantityVal']
        prodId = request.form['prodId']
        productPrice = Product.query.get(prodId)
        money = productPrice.price
        totalPrice = money*int(quantityNum)
        cartQuan=Cart.query.filter_by(userId=current_user.userId,product_id=prodId).first()
        cartQuan.quantity = quantityNum
        db.session.commit()
        overallPrice=0
        for cart_row in Cart.query.filter_by(userId = current_user.userId).all():
                for rows in Product.query.all():
                    if cart_row.product_id == rows.id:
                        overallPrice = (cart_row.quantity*rows.price)+overallPrice
        return jsonify({'status':'OK','totalPrice': format_price(totalPrice), 'overallPrice':format_price(overallPrice)})
    else:
        return render_template(
            'single-store/cart-page.djhtml', message=message
            )
        

@app.route("/checkout")
@login_required
def checkout():
    return render_template(
        'single-store/checkout-page.djhtml'
        )

@app.route("/wishlist")
@login_required
def wishlist():
    message = "Your wishlist is empty"
    wishlist_products = Wishlist.query.filter(Wishlist.userId == current_user.userId).first()
    product_lists = wishlist_products.product_list
    product_lists = product_lists.split(",")
    return render_template(
        'single-store/wishlist-page.djhtml', product_lists = product_lists, message= message
        )

@app.route("/compare")
@login_required
def compare():
    compare_products = Compare.query.filter(Compare.userId == current_user.userId).first()
    message = "There's no product to compare"
    if compare_products is None:
        print("Add Some Products to compare first")
        product_lists = ""
    else:
        product_lists = compare_products.product_list
        product_lists = product_lists.split(",")

    return render_template(
        'single-store/compare-page.djhtml', product_lists = product_lists, message=message
        )

@app.route("/track-order")
@login_required
def track_order():
    return render_template(
        'single-store/track-order-page.djhtml'
        )

@app.route("/category")
@login_required
def products_archive():
    return render_template(
        'single-store/products-archive-page.djhtml'
        )

@app.route("/order-success")
@login_required
def order_success():
    return render_template(
        'single-store/order-success-page.djhtml'
        )

@app.route("/quickviewProduct", methods = ['POST'])
def quickviewProduct():
    if request.method == "POST":
        id = int(request.get_data())
        quickViewProductData = Product.query.get(id)
    return render_template(
        'general/blocks/quick-view-modal-block.djhtml', product = quickViewProductData,
        )

@app.route("/searchSuggestion", methods=['POST'])
def searchSuggestion():
    if request.method == "POST":
        selectedCategory = request.form.get("category")
        search_word = request.form.get("keyword")
        filters =[]
        if selectedCategory:
            filters.append(
                Product.category == selectedCategory
            )
        search_product = Product.query.filter(*filters,Product.productName.ilike('%'+search_word+'%')).limit(6).all()

    return render_template(
        'general/header/search-suggestion.djhtml', search_product=search_product
        )

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template(
        'admin/dashboard-page.djhtml'
        )

@app.route("/add-products")
def admin_add_products():
    return render_template(
        'admin/add-products-page.djhtml'
        )

@app.route("/view-products")
def admin_products_listing():
    return render_template(
        'admin/product-listing-page.djhtml'
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
                flash('Failed to Create Account', 'danger')

    return render_template(
        'single-store/user-account/user-account.djhtml', form1=form1, form2 = form2
        )

@app.route("/dashboard")
@login_required
def user_dashboard():
    userAddress = Shipping.query.filter_by(userId = current_user.userId,status=True).first()
    return render_template(
        'single-store/user-account/dashboard-page.djhtml', userAddress=userAddress
        )

@app.route("/dashboard/edit-profile", methods=['POST','GET'])
@login_required
def edit_profile():
    user = User.query.get(current_user.userId)
    if request.method == 'POST':
        user.firstName = request.form['firstName']
        user.lastName = request.form['lastName']
        user.email = request.form['email']
        db.session.commit()
        return jsonify({'status':'OK','firstName' : request.form['firstName']})

    else:
        formSend=EditDashboardProfileForm()
        if request.method == 'GET':
            formSend.firstName.data = user.firstName
            formSend.lastName.data = user.lastName
            formSend.email.data = user.email
        return render_template(
            'single-store/user-account/edit-profile-page.djhtml', form = formSend
            )


@app.route("/dashboard/order-history")
@login_required
def order_history():
    return render_template(
        'single-store/user-account/order-history-page.djhtml'
        )

@app.route("/dashboard/order-details")
@login_required
def order_details():
    return render_template(
        'single-store/user-account/order-details-page.djhtml'
        )

@app.route("/dashboard/address-book", methods=["POST","GET"])
@login_required
def address_book():
    if request.method == "POST":    #to delete the addreess block
        shipId = int(request.get_data())
        if Shipping.query.filter_by(id=shipId).delete():
            db.session.execute("ALTER SEQUENCE shipping_id_seq RESTART")
            db.session.commit()
        return jsonify({'status':'OK'})
    else:
        userAddress = Shipping.query.filter_by(userId = current_user.userId).all()
        return render_template(
            'single-store/user-account/address-book-page.djhtml', userAddress=userAddress
            )

@app.route("/dashboard/address-book/ChangeStatus", methods=["POST"])
@login_required
def changeStatus():
    if request.method == "POST":
        shipId = int(request.get_data())
        for rows in Shipping.query.filter_by(userId = current_user.userId).all():
            rows.status = False
            db.session.commit()
        ship = Shipping.query.filter_by(id = shipId ,userId = current_user.userId).first()
        ship.status = True
        db.session.commit()
    return jsonify({'status':'OK'})

@app.route("/dashboard/edit-address", methods=['POST','GET'])
@login_required
def addAddress():
    formSend=EditDashboardAddressForm()
    if request.method == "POST":
        statusVal=False
        if (Shipping.query.filter_by(userId = current_user.userId).count() == 0):
                statusVal=True
        addShipping = Shipping(
            firstName = request.form['firstName'],
            lastName = request.form['lastName'],
            companyName = request.form['companyName'],
            country = request.form['country'],
            street = request.form['street'],
            houseCode = request.form['houseCode'],
            city = request.form['city'],
            state = request.form['state'],
            postalCode = request.form['postalCode'],
            phoneNo = request.form['phoneNo'],
            altPhoneNo = request.form['altPhoneNo'],
            userId = current_user.userId,
            status=statusVal,
            )
        db.session.add(addShipping)
        db.session.commit()
        return jsonify({'status':'added','firstName' : request.form['firstName']})
    else:
        return render_template(
            'single-store/user-account/edit-address-page.djhtml', form = formSend
            )

@app.route("/dashboard/edit-address/<int:shipId>", methods=["POST","GET"])
@login_required
def editAddress(shipId):
    ship = Shipping.query.filter_by(id=shipId,userId=current_user.userId).first()
    if request.method == 'POST':
        ship.firstName = request.form['firstName']
        ship.lastName = request.form['lastName']
        ship.companyName = request.form['companyName']
        ship.country = request.form['country']
        ship.street = request.form['street']
        ship.houseCode = request.form['houseCode']
        ship.city = request.form['city']
        ship.state = request.form['state']
        ship.postalCode = request.form['postalCode']
        ship.phoneNo = request.form['phoneNo']
        ship.altPhoneNo = request.form['altPhoneNo']

        db.session.commit()
        return jsonify({'status':'updated','firstName' : request.form['firstName']})

    else:
        formSend=EditDashboardAddressForm()
        if request.method == 'GET':
            formSend.firstName.data = ship.firstName
            formSend.lastName.data = ship.lastName
            formSend.companyName.data = ship.companyName
            formSend.country.data = ship.country
            formSend.street.data = ship.street
            formSend.houseCode.data = ship.houseCode
            formSend.city.data = ship.city
            formSend.state.data = ship.state
            formSend.postalCode.data = ship.postalCode
            formSend.phoneNo.data = ship.phoneNo
            formSend.altPhoneNo.data = ship.altPhoneNo
        return render_template(
            'single-store/user-account/edit-address-page.djhtml', form = formSend
            )

@app.route("/dashboard/change-password", methods=["POST","GET"])
@login_required
def change_password():
    form = DashboardPwForm()
    result=''   #declared to pass empty string
    if request.method == 'POST' and form.validate():
        formOldPassword = form.oldPw.data
        formNewPassword = form.newPw.data
        userAc = User.query.get(current_user.userId)
        dbPassword = userAc.password
        print(formOldPassword,'-->',dbPassword,'<<>>>',formNewPassword)
        if bcrypt.check_password_hash(dbPassword, formOldPassword) == True:
            hashed_newFormPassword = bcrypt.generate_password_hash(formNewPassword).decode('utf-8')
            userAc.password = hashed_newFormPassword
            db.session.commit()
            flash('Thanks for registering')
            return redirect(url_for('user_dashboard'))
        else:
            print('wrong password entered')
            result ='you entered wrong old password'
    return render_template(
        'single-store/user-account/change-password-page.djhtml', form= form, result = result
        )


@app.route("/about")
def about():
    return render_template('about.html', title='About')


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


# @app.route("/add_product", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def add_product():

#     product_table = Product()
#     form = ProductForm()
#     form.category.choices = [(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
#     form.brand.choices = [(brand.name) for brand in Brand.query.with_entities(Brand.name).all()]
#     if form.validate_on_submit():
        
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             featuredImage = save_picture(form.imageFile.data, random_hex + form.productName.data, 'products', 700, 700)
            
#         if form.imageGallery.data:
#             galleryImages = ""
#             file_list = request.files.getlist('imageGallery')
#             print(file_list)
#             for f in file_list:
#                 random_hex = secrets.token_hex(4)
#                 file_name = f
#                 images = save_picture(file_name, random_hex + form.productName.data, 'gallery', 700, 700)
#                 galleryImages = galleryImages + "," + images

#         if request.form.get('submit'):
#             product = Product(productName = form.productName.data, 
#                             slug = form.slug.data,
#                             price=form.price.data, 
#                             discount=form.discount.data,
#                             stock = form.stock.data,
#                             category = form.category.data,
#                             brand = form.brand.data,
#                             color = form.color.data,
#                             size = form.size.data,
#                             weight = form.weight.data,
#                             dimension = form.dimension.data,
#                             material = form.material.data,
#                             shortDescription = form.shortDescription.data,
#                             longDescription = form.longDescription.data,
#                             imageFile = featuredImage,
#                             imageGallery = galleryImages,
#                             tags = form.tags.data,
#                             badgeDuration = form.badgeDuration.data,
#                             excludeBadge = form.excludeBadge.data,
#                             featured = form.featured.data,
#                             product_user_id = current_user,
#                             )
#             print(product)
#             db.session.add(product)
#             db.session.commit()
#             flash(form.productName.data+' Product Added Successful!', 'success')
#         else:
#             # form.productName.data = 
#             # form.email.data = current_user.email
#             flash('Product Edited Successful!', 'success')
#             # return redirect(url_for('home'))

#     # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
#     return render_template('add_product.html', title='New Product', form=form)


# @app.route("/edit_product/<int:productId>", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def edit_product(productId):
#     product = Product.query.get_or_404(productId)
#     form = EditProductForm()
#     form.category.choices = [(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
#     form.brand.choices = [(brand.name) for brand in Brand.query.with_entities(Brand.name).all()]
#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             featuredImage = save_picture(form.imageFile.data, random_hex + form.productName.data, 'products', 700, 700)
#             print(featuredImage)

#         if form.imageGallery.data:
#             galleryImages = ""
#             file_list = request.files.getlist('imageGallery')
#             print(file_list)
#             for f in file_list:
#                 random_hex = secrets.token_hex(4)
#                 file_name = f
#                 images = save_picture(file_name, random_hex + form.productName.data, 'gallery', 700, 700)
#                 galleryImages = galleryImages + "," + images

#         if request.form.get('submit'):
#             product.productName = form.productName.data
#             product.slug = form.slug.data
#             product.price = form.price.data
#             product.discount = form.discount.data
#             product.stock = form.stock.data
#             product.category = form.category.data
#             product.brand = form.brand.data
#             product.color = form.color.data
#             product.size = form.size.data
#             product.weight = form.weight.data
#             product.dimension = form.dimension.data
#             product.material = form.material.data
#             product.shortDescription = form.shortDescription.data
#             product.longDescription = form.longDescription.data
#             product.imageFile = featuredImage
#             product.imageGallery = galleryImages,
#             product.tags = form.tags.data
#             product.badgeDuration = form.badgeDuration.data
#             product.excludeBadge = form.excludeBadge.data
#             product.featured = form.featured.data
#             product.product_user_id = current_user
#             db.session.commit()
#             flash(form.productName.data+' Product Updated Successful!', 'success')
#     elif request.method == 'GET' :
#         #db data are fetch in form in this method
#         form.productName.data = product.productName 
#         form.slug.data = product.slug 
#         form.price.data = product.price
#         form.discount.data = product.discount
#         form.stock.data = product.stock
#         form.category.data = product.category
#         form.brand.data = product.brand
#         form.color.data = product.color
#         form.size.data  = product.size
#         form.weight.data = product.weight 
#         form.dimension.data = product.dimension 
#         form.material.data = product.material 
#         form.shortDescription.data = product.shortDescription 
#         form.longDescription.data = product.longDescription
#         form.imageFile.data = product.imageFile
#         form.imageGallery.data = product.imageGallery
#         form.tags.data = product.tags 
#         form.badgeDuration.data = product.badgeDuration
#         form.excludeBadge.data = product.excludeBadge
#         form.featured.data = product.featured
#     return render_template('edit_product.html', title= product.productName, form=form)


# @app.route("/add_category", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def add_category():

#     category_table = Category()
#     form = CategoryForm()
#     form.parentCategory.choices = ['None']+[(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
    
#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             image = save_picture(form.imageFile.data, random_hex + form.name.data, 'category', 700, 700)

#         if request.form.get('submit'):
#             category = Category(name = form.name.data, 
#                             slug = form.slug.data,
#                             parentCategory = form.parentCategory.data,
#                             description = form.description.data,
#                             imageFile = image,
#                             )
#             db.session.add(category)
#             db.session.commit()
#             flash('Category Added Successful!', 'success')
        
#         # return redirect(url_for('home'))

#     # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
#     return render_template('add_category.html', title='New Category', form=form)



# @app.route("/edit_category/<int:categoryId>", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def edit_category(categoryId):
#     category = Category.query.get_or_404(categoryId)
#     form = EditCategoryForm()
#     form.parentCategory.choices = ['None']+[(category.name) for category in Category.query.with_entities(Category.name).all()]
#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             image = save_picture(form.imageFile.data, random_hex + form.name.data, 'category', 700, 700)

#         if request.form.get('submit'):
#             category.name = form.name.data
#             category.slug = form.slug.data
#             category.parentCategory = form.parentCategory.data
#             category.description = form.description.data
#             category.imageFile = image
#             db.session.commit()
#             flash(form.name.data+' Category Updated Successful!', 'success')
#     elif request.method == 'GET' :
#         form.name.data = category.name 
#         form.slug.data = category.slug
#         form.parentCategory.data = category.parentCategory
#         form.description.data = category.description
#         form.imageFile.data = category.imageFile                      
#     return render_template('edit_category.html', title=category.name, form=form)



# @app.route("/add_brand", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def add_brand():

#     brand_table = Brand()
#     form = BrandForm()
        
#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             image = save_picture(form.imageFile.data,random_hex + form.name.data, 'brand', 700, 700)

#         if request.form.get('submit'):
#             brand = Brand(name = form.name.data, 
#                             slug = form.slug.data,
#                             description = form.description.data,
#                             imageFile = image,
#                             )
#             db.session.add(brand)
#             db.session.commit()
#             flash(form.name.data+' Brand Added Successful!', 'success')
        
#         # return redirect(url_for('home'))

#     # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
#     return render_template('add_brand.html', title='New Brand', form=form)

# @app.route("/edit_brand/<int:brandId>", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def edit_brand(brandId):

#     brand = Brand.query.get_or_404(brandId)
#     form = EditBrandForm()

#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             image = save_picture(form.imageFile.data,random_hex + form.name.data, 'brand', 700, 700)
        
#         if request.form.get('submit'):
#             brand.name = form.name.data
#             brand.slug = form.slug.data
#             brand.description = form.description.data
#             brand.imageFile = image
#             db.session.commit()
#             flash(form.name.data+' Brand Updated Successful!', 'success')
    
#     elif request.method == 'GET' :
#         form.name.data = brand.name 
#         form.slug.data = brand.slug  
#         form.description.data = brand.description 
#         form.imageFile.data = brand.imageFile 
#     return render_template('edit_brand.html', title=brand.name, form=form)

# @app.route("/add_hero", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def add_hero():

#     hero_table = Hero()
#     form = HeroForm()
        
#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             image = save_picture(form.imageFile.data, random_hex + form.title.data, 'hero/desktop', 840, 395)
#             image = save_picture(form.imageFile.data, random_hex + form.title.data, 'hero/mobile', 510, 395)

#         if request.form.get('submit'):
#             hero = Hero(title = form.title.data, 
#                             description = form.description.data,
#                             button = form.button.data,
#                             imageFile =image,
#                             )
#             db.session.add(hero)
#             db.session.commit()
#             flash(form.title.data+' Hero section Added Successful!', 'success')
        
#         # return redirect(url_for('home'))

#     # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
#     return render_template('add_hero.html', title='New Hero', form=form)

# @app.route("/edit_hero/<int:heroId>", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def edit_hero(heroId):

#     hero=Hero.query.get_or_404(heroId)
#     form = EditHeroForm()
        
#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             image = save_picture(form.imageFile.data, random_hex + form.title.data, 'hero/desktop', 840, 395)
#             image = save_picture(form.imageFile.data, random_hex + form.title.data, 'hero/mobile', 510, 395)

#         if request.form.get('submit'):
#             hero.title = form.title.data
#             hero.description = form.description.data
#             hero.button = form.button.data
#             hero.imageFile =image
#             db.session.commit()
#             flash(form.title.data+' Hero section Updated Successful!', 'success')

#     elif request.method == 'GET' :
#         form.title.data = hero.title 
#         form.description.data = hero.description  
#         form.button.data = hero.button 
#         form.imageFile.data = hero.imageFile
#     return render_template('edit_hero.html', title=hero.title, form=form)

# @app.route("/add_feature", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def add_feature():

#     features_table = Features()
#     form = FeaturesForm()
        
#     if form.validate_on_submit():

#         if request.form.get('submit'):
#             feature = Features(title = form.title.data, 
#                             description = form.description.data,
#                             icon = form.icon.data,
#                             )
#             db.session.add(feature)
#             db.session.commit()
#             flash('Feature Added Successful!', 'success')
        
#         # return redirect(url_for('home'))

#     # image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
#     return render_template('add_feature.html', title='New Feature', form=form)

# @app.route("/edit_feature/<int:featureId>", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def edit_feature(featureId):
#     features=Features.query.get_or_404(featureId)
#     form = EditFeaturesForm()
        
#     if form.validate_on_submit():

#         if request.form.get('submit'):
#             features.title = form.title.data
#             features.description = form.description.data
#             features.icon = form.icon.data
#             db.session.commit()
#             flash(form.title.data+' Feature Added Successful!', 'success')

#     elif request.method == 'GET':
#         form.title.data = features.title
#         form.description.data = features.description
#         form.title.icon = features.icon
#     return render_template('edit_feature.html', title=form.title.data, form=form)

# @app.route("/add_horizontalpanel", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def add_horizontal():

#     horizontal_table = HorizontalPanel()
#     form = HorizontalPanelForm()
        
#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             image = save_picture(form.imageFile.data, random_hex + form.title.data, 'horizontalPanel/desktop', 1110, 170)
#             image = save_picture(form.imageFile.data, random_hex + form.title.data, 'horizontalPanel/mobile', 510, 390)

#         if request.form.get('submit'):
#             horizontal = HorizontalPanel(title = form.title.data, 
#                             description = form.description.data,
#                             button = form.button.data,
#                             imageFile =image,
#                             )
#             db.session.add(horizontal)
#             db.session.commit()
#             flash(form.title.data+' Horizontal Panel section Added Successful!', 'success')
#     return render_template('add_horizontalPanel.html', title='New Horizontal Panel', form=form)

# @app.route("/edit_horizontal/<int:horizontalId>", methods=['GET', 'POST'])
# @login_required
# @restricted(access_level="Admin")
# def edit_horizontal(horizontalId):

#     horizontal=HorizontalPanel.query.get_or_404(horizontalId)
#     form = EditHorizontalPanelForm()
        
#     if form.validate_on_submit():
#         if form.imageFile.data:
#             random_hex = secrets.token_hex(4)
#             image = save_picture(form.imageFile.data, random_hex + form.title.data, 'horizontalPanel/desktop', 840, 395)
#             image = save_picture(form.imageFile.data, random_hex + form.title.data, 'horizontalPanel/mobile', 510, 395)

#         if request.form.get('submit'):
#             horizontal.title = form.title.data
#             horizontal.description = form.description.data
#             horizontal.button = form.button.data
#             horizontal.imageFile =image
#             db.session.commit()
#             flash(form.title.data+' horizontal panel Updated Successful!', 'success')

#     elif request.method == 'GET' :
#         form.title.data = horizontal.title 
#         form.description.data = horizontal.description  
#         form.button.data = horizontal.button 
#         form.imageFile.data = horizontal.imageFile
#     return render_template('edit_horizontalPanel.html', title=horizontal.title, form=form)

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
    tables = tables.capitalize()
    if tables == 'Horizontalpanel':
        tables="HorizontalPanel"
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
    tables = tables.capitalize()
    if tables == 'Horizontalpanel':
        tables="HorizontalPanel"
    table = str2Class(tables)
    table_name = tables.lower()
    if table.query.filter_by(id=id).delete():
        db.session.execute("ALTER SEQUENCE "+ table_name +"_id_seq RESTART")
        db.session.commit()
        print("Success")
    else:
        print("Failed")
    return redirect('/lists/'+tables)


def format_price(amount, currency='Rs. '):
    currency = request.cookies.get('currency')
    if currency is None:
        currency = "NPR"
    if currency == "USD" or currency == "EUR":
        amount = amount / 1.6
        c = CurrencyConverter()
        if currency == "USD":
            amount = c.convert(amount, 'INR', 'USD')
        elif currency == "EUR":
            amount = c.convert(amount, 'INR', 'EUR')
        amount = "{:,.2f}".format(amount)
    else:
        amount_list = [int(d) for d in str(amount)]
        amount_list.reverse()
        list_length = len(amount_list)
        for i in range(1, int(list_length/2)):
            amount_list.insert(3*i,",")

        amount_list.reverse()
        amount = ''.join([str(elem) for elem in amount_list])
        amount = amount+".00"

    return '{1} {0}'.format(amount, currency)


@app.route("/add_cart", methods=["POST"])

def add_Cart():
    if request.method == "POST" and current_user.is_authenticated:
        productId = request.form['cart_index']
        quantityValue = int(request.form['quantityVal'])
        product= Product.query.get(productId)
        cart=Cart.query.filter_by(product_id=productId).first()
        if cart is None:
            if product.stock>=quantityValue:
                addCart = Cart(
                            quantity =quantityValue,
                            color = product.color,
                            size = product.size,
                            cart_user_id = current_user,
                            cart_product_id=product,
                            )
                db.session.add(addCart)
                db.session.commit()
            else:
                print("quantity selected more than the stock-> ",product.productName)
        else:
            if (product.stock>=cart.quantity+quantityValue):
                quantityValue = cart.quantity+quantityValue
                db.session.query(Cart).filter(Cart.product_id == productId).update({'quantity':quantityValue}, synchronize_session=False)
                db.session.commit()
            else:
                print(" quantity selected more than the stock -> ",product.productName)
        products = Product.query.all()
        cart_data = Cart.query.filter_by(userId = current_user.userId).all()
        cart_count = len(cart_data)
        totalCart = 0
        for cart_row in cart_data:
            for rows in products:
                if cart_row.product_id == rows.id:
                    totalCart = (cart_row.quantity*rows.price)+totalCart
        totalCart = format_price(totalCart)

        return jsonify({'htmlresponse':render_template('single-store/sidebar-cart.djhtml', cart=cart_data), 
                    'cart_count':cart_count,
                    'totalCart' :totalCart
                })
    else:
        print("Please Login To Continue")
        flash("Please Login To Add To Cart", "danger")
        return ('', 204)

@app.route("/delete_cart", methods=["POST"])
@login_required
def deleteCart():
    if request.method == "POST":
        productId= int(request.get_data())
    if Cart.query.filter_by(product_id=productId).delete():
        db.session.execute("ALTER SEQUENCE cart_id_seq RESTART")
        db.session.commit()
        print("Success")
    else:
        print("Failed")
    cart = Cart.query.filter_by(userId = current_user.userId).all()
    products = Product.query.all()
    totalCart = 0
    cartProductNumber = 0
    for cart_row in cart:
        for rows in products:
            if cart_row.product_id == rows.id:
                totalCart = (cart_row.quantity*rows.price)+totalCart
                cartProductNumber=cartProductNumber+1
    totalCart = format_price(totalCart)
    return jsonify({'result': 'success', 'cartProductNumber':cartProductNumber, 'totalCart':totalCart})


@app.route("/wishlistAdd", methods=['POST', 'GET'])
def addWishlist():

    if request.method == "POST" and current_user.is_authenticated:
        productId= int(request.get_data())

        wishlist_list = Wishlist.query.filter_by(userId = current_user.userId).first()
        if wishlist_list is None:
            add_wishlist = Wishlist(
                                product_list = productId,
                                wishlist_user_id = current_user,
                                )
            db.session.add(add_wishlist)
            db.session.commit()

        else:
            product_l = wishlist_list.product_list
            if product_l == "":
                actual_data = {'product_list':productId}
                db.session.query(Wishlist).filter(Wishlist.userId == current_user.userId).update(actual_data, synchronize_session=False)
                db.session.commit()

            else:
                list_product = wishlist_list.product_list.split(",")
                count = len(list_product)
                for i in range(count):
                    if int(list_product[i]) == productId:
                        print("Already In Wishlist")
                        break
                    elif i+1 == count:
                        data = wishlist_list.product_list + "," +str(productId)
                        actual_data = {'product_list':data}
                        db.session.query(Wishlist).filter(Wishlist.userId == current_user.userId).update(actual_data, synchronize_session=False)
                        db.session.commit()

        indicators = Wishlist.query.filter_by(userId = current_user.userId).first()
        list_product = indicators.product_list.split(",")
        wishlist_indicator = len(list_product)
        return jsonify({'result': 'success', 'wishlist_indicator': wishlist_indicator})
    else:
        print("Please Login To Continue")
        return redirect("/")

@app.route("/users/<tables>", methods = ['POST'])
@login_required
def delete_wishlist(tables):
    urll = tables
    tables = tables.capitalize()
    table_name = str2Class(tables)
    if request.method == "POST":
        id = int(request.get_data())
    product_list = table_name.query.filter_by(userId = current_user.userId).first()
    list_product = product_list.product_list.split(",")
    list_product.remove(str(id))
    listToStr = ','.join([str(elem) for elem in list_product])
    db.session.query(table_name).filter(table_name.userId == current_user.userId).update({'product_list':listToStr}, synchronize_session=False)
    db.session.commit()
    indicators = table_name.query.filter_by(userId = current_user.userId).first()
    list_product = indicators.product_list.split(",")
    if list_product[0] == '':
            indicator = 0
    else:
        indicator = len(list_product)

    return jsonify({'result': 'success', 'indicator': indicator})


@app.route("/compare_add", methods=["POST"])

def addCompare():
    if request.method == "POST" and current_user.is_authenticated:
        productId = int(request.get_data())
        compare_list = Compare.query.filter(Compare.userId == current_user.userId).first()

        if compare_list is None:
            add_compare = Compare(
                                product_list = productId,
                                compare_user_id = current_user,
                                )
            db.session.add(add_compare)
            db.session.commit()

        else:
            product_l = compare_list.product_list
            if product_l == "":
                actual_data = {'product_list':productId}
                db.session.query(Compare).filter(Compare.userId == current_user.userId).update(actual_data, synchronize_session=False)
                db.session.commit()
            else:
                list_product = compare_list.product_list.split(",")
                count = len(list_product)
                for i in range(count):
                    if int(list_product[i]) == productId:
                        print("Already in Compare List")
                        break
                    elif i+1 == count:
                        data = compare_list.product_list + "," +str(productId)
                        actual_data = {'product_list':data}
                        db.session.query(Compare).filter(Compare.userId == current_user.userId).update(actual_data, synchronize_session=False)
                        db.session.commit()
        # return ('', 204)
        return jsonify({'result': 'success'})
    else:
        print("Please Login To Continue")
        return redirect("/")

@app.route("/add/<tables>", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def add(tables):
    tables = tables.capitalize()
    table_name = str2Class(tables)
    table_head = table_name.__table__.columns.keys()

    slug = db.session.query(table_name.slug).all()
    slug = [value for value, in slug]

    form_name = tables+"Form"
    formName = str2Class(form_name)
    form = formName()

    form_data = {formfield : value for formfield, value in form.data.items()}
    for formfield, value in form.data.items():
        if formfield == 'category':
            form.category.choices = [(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
        if formfield == 'brand':
            form.brand.choices = [(brand.name) for brand in Brand.query.with_entities(Brand.name).all()]
        if formfield == 'parentCategory':
            form.parentCategory.choices = ['None']+[(category.name) for category in Category.query.with_entities(Category.name).all()]
    if form.validate_on_submit():
        data = {formfield : value for formfield, value in form.data.items()}
        data.popitem()
        data.popitem()

        for formfield, value in form.data.items():
            if formfield == 'imageFile':
                if form.imageFile.data:
                    random_hex = secrets.token_hex(4)
                    f = form.imageFile.data
                    file = f.filename.replace(" ", "_")
                    split_name = file.split(".")
                    if tables == "Category":
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'category', 700, 700)
                    elif tables == "Hero":
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'hero/desktop', 840, 395)
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'hero/mobile', 510, 395)
                    elif tables == "Brand":
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'brand', 700, 700)
                    elif tables == "HorizontalPanel":
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'horizontalpanel/desktop', 1110, 170)
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'horizontalpanel/mobile', 510, 390)
                    else:
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'products', 700, 700)
                    featuredImage = secure_filename(featuredImage)
                    data['imageFile'] = featuredImage

            if formfield == 'imageGallery':
                if form.imageGallery.data:
                    galleryImages = featuredImage
                    # file_list = request.files.getlist('imageGallery')
                    for f in form.imageGallery.data:
                        if f.filename == '':
                            break
                        random_hex = secrets.token_hex(4)
                        file = f.filename.replace(" ", "_")
                        split_name = file.split(".")
                        images = save_picture(f, split_name[0]+random_hex+ split_name[1], 'gallery', 700, 700)
                        img = secure_filename(images)
                        galleryImages = galleryImages + "," + img

                    data['imageGallery'] = galleryImages

        actual_data = data
        dt = datetime.now(timezone.utc)
        actual_data['dateCreated'] = dt
        actual_data['userId'] = current_user.userId
        table_db = tables.lower()
        
        insert_table = table(table_db,
                         *[column(field) for field in table_head[1:]])
        insert_dict = [actual_data]
        db.session.execute(insert_table.insert(), insert_dict)
        db.session.commit()

        flash('Feature Added Successful!', 'success')
        
    return render_template('add.html', title=tables, form=form, slug=slug)


@app.route("/edit/<tables>/<int:id>", methods=['GET', 'POST'])
@login_required
@restricted(access_level="Admin")
def edit(tables, id):
    tables = tables.capitalize()
    table_name = str2Class(tables)
    table_head = table_name.__table__.columns.keys()

    slug = db.session.query(table_name.slug).all()
    slug = [value for value, in slug]


    form_name = tables+"Form"
    formName = str2Class(form_name)
    form = formName()

    form_data = {formfield : value for formfield, value in form.data.items()}
    for formfield, value in form.data.items():
        if formfield == 'category':
            form.category.choices = [(category.name) for category in Category.query.with_entities(Category.name).all()] #db.session.query(Category.name)
        if formfield == 'brand':
            form.brand.choices = [(brand.name) for brand in Brand.query.with_entities(Brand.name).all()]
        if formfield == 'parentCategory':
            form.parentCategory.choices = ['None']+[(category.name) for category in Category.query.with_entities(Category.name).all()]
    if form.validate_on_submit():
        data = {formfield : value for formfield, value in form.data.items()}
        data.popitem()
        data.popitem()

        for formfield, value in form.data.items():
            if formfield == 'imageFile':
                if form.imageFile.data:
                    random_hex = secrets.token_hex(4)
                    f = form.imageFile.data
                    file = f.filename.replace(" ", "_")
                    split_name = file.split(".")
                    if tables == "Category":
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'category', 700, 700)
                    elif tables == "Hero":
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'hero/desktop', 840, 395)
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'hero/mobile', 510, 395)
                    elif tables == "Brand":
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'brand', 700, 700)
                    elif tables == "HorizontalPanel":
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'horizontalpanel/desktop', 1110, 170)
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'horizontalpanel/mobile', 510, 390)
                    else:
                        featuredImage = save_picture(f, split_name[0]+random_hex+ split_name[1], 'products', 700, 700)
                    featuredImage = secure_filename(featuredImage)
                    data['imageFile'] = featuredImage

            if formfield == 'imageGallery':
                if form.imageGallery.data:
                    galleryImages = featuredImage
                    # file_list = request.files.getlist('imageGallery')
                    for f in form.imageGallery.data:
                        random_hex = secrets.token_hex(4)
                        file = f.filename.replace(" ", "_")
                        split_name = file.split(".")
                        images = save_picture(f, split_name[0]+random_hex+ split_name[1], 'gallery', 700, 700)
                        img = secure_filename(images)
                        galleryImages = galleryImages + "," + img

                    data['imageGallery'] = galleryImages

        actual_data = data
        dt = datetime.now(timezone.utc)
        # actual_data['dateCreated'] = dt
        # actual_data['userId'] = current_user.userId

        db.session.query(table_name).filter(table_name.id == id).update(actual_data, synchronize_session=False)
        db.session.commit()

        flash('Feature Added Successful!', 'success')
        
    

    table_object = table_name.query.get_or_404(id)
    
    a = {}
    for items, value in table_object.__dict__.items():
        a[items] = value

    return render_template('edit.html', title=tables, form=form, table_head=table_head, product_dict=a, slug = slug)

 
@app.route('/forget-password')
def forget():
    if current_user.is_authenticated:
        return redirect('/account')
    else:
        return render_template('single-store/forget-password.html')


@app.route('/send-otp', methods = ['POST'])
def send_otp():
    if request.method == "POST":
        email = request.form.get('email')
        otp = request.form.get('otp')
        registered_email = User.query.filter(User.email == email).first()
        if registered_email is None:
            error = True
            
        else:
            error = False
            msg = Message(subject="Hello",
                        sender=app.config.get("MAIL_USERNAME"),
                        recipients=[email], # replace with your email for testing
                        body="Use this OTP to change your password"+str(otp)+"This OTP will be valid for 60 Seconds")
            mail.send(msg)
        
    return jsonify({"otp": otp, "error": error, "reg_email":email, "userId":registered_email.userId})

@app.route('/change-password/<int:access_code>', methods=['POST', 'GET'])
def forgetPassword(access_code):
    cookie_access_code = request.cookies.get('access_code')
    if access_code == int(cookie_access_code):
        form = ForgetPassword()
        if form.validate_on_submit():
            selectedId = request.cookies.get('id')
            user = User.query.get(selectedId)
            hashed_password = bcrypt.generate_password_hash(form.newPw.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Password Change Successful. Please Login to continue', 'success')
            return redirect('/account')
        else:
            flash('Failed to change Password', 'success')
        return render_template('single-store/change-password.html', form=form)
    else:
        return redirect('/account')