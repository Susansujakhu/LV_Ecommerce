

from enum import unique
from flask.helpers import url_for
from werkzeug.utils import redirect
from ecommerce import db, login_manager
from flask_login import UserMixin, current_user
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class AdminView(ModelView):


    def is_accessible(self):
        return current_user.role == "Admin"
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    userId = db.Column(db.Integer, primary_key = True)
    userName = db.Column(db.Text, unique = True, nullable = False)
    email = db.Column(db.Text, unique = True, nullable = False)
    imageFile = db.Column(db.Text, nullable = False, default = 'default.jpg')
    password = db.Column(db.Text, nullable = False)
    role = db.Column(db.Text, nullable = False, default = 'Customer')
    dateRegistered = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    # For relation with Shipping database table
    shippingDetails = db.relationship('Shipping', backref = 'shipping_user_id', lazy = True) 
    # post = Post(title = form.title.data, content = form.content.data, user = current_user)
    productId = db.relationship('Product', backref = 'product_user_id', lazy = True) 
    userCart = db.relationship('Cart', backref = 'cart_user_id', lazy = True) 
    userOrder = db.relationship('Order', backref = 'order_user_id', lazy = True) 
    userRating = db.relationship('Rating', backref = 'rating_user_id', lazy = True) 

    def get_id(self):
        return (self.userId)

    def __repr__(self):
        return f"User('{self.userName}', '{self.email}', '{self.imageFile}', '{self.role}', '{self.dateRegistered}')"


class Shipping(db.Model):
    __tablename__ = 'shipping'
    id = db.Column(db.Integer, primary_key = True)
    fullName = db.Column(db.Text, nullable = False)
    contactNo = db.Column(db.Text, nullable = True)
    phoneNo = db.Column(db.Text, nullable = False)
    street = db.Column(db.Text, nullable = False)
    city = db.Column(db.Text, nullable = False)
    country = db.Column(db.Text, nullable = False)

    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable = False)


    def __repr__(self):
        return f"Post('{self.fullName}', '{self.contactNo}', '{self.phoneNo}', '{self.street}', '{self.city}', '{self.country}')"


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key = True)
    productName = db.Column(db.Text, nullable = False)
    slug = db.Column(db.Text, nullable = False, unique = True)
    price = db.Column(db.Integer, nullable = False)                        
    discount = db.Column(db.Integer, nullable = True)
    stock = db.Column(db.Integer, nullable = False, default = 1)
    category = db.Column(db.Text, nullable = False)
    brand = db.Column(db.Text, nullable = True)
    color = db.Column(db.String(50), nullable = True)
    size = db.Column(db.String(50), nullable = True)
    weight = db.Column(db.String(50), nullable = True)
    dimension = db.Column(db.String(50), nullable = True)
    material = db.Column(db.String(50), nullable = True)
    shortDescription = db.Column(db.Text, nullable = True)
    longDescription = db.Column(db.Text, nullable = True)
    imageFile = db.Column(db.Text, nullable = False, default = 'default.jpg')
    imageGallery = db.Column(db.Text, nullable = True)
    featured = db.Column(db.Boolean, nullable = False, default = False)

    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable = False) # User Id

    productCart = db.relationship('Cart', backref = 'cart_product_id', lazy = True) 
    productOrder = db.relationship('Order', backref = 'order_product_id', lazy = True) 
    productRating = db.relationship('Rating', backref = 'rating_product_id', lazy = True) 
    

    def __repr__(self):
        return f"Post('{self.productName}','{self.price}','{self.discount}','{self.stock}','{self.category}','{self.brand}','{self.color}','{self.size}','{self.weight}','{self.dimension}','{self.material}','{self.shortDescription}','{self.longDescription}','{self.imageFile}','{self.imageGallery}','{self.featured}')"


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Integer, nullable = False)
    color = db.Column(db.String(10), nullable = True)
    size = db.Column(db.String(10), nullable = True)

    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)
    
    def __repr__(self):
        return f"Post('{self.quantity}', '{self.color}', '{self.size}')"


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Integer, nullable = False)
    color = db.Column(db.String(10), nullable = True)
    size = db.Column(db.String(10), nullable = True)
    status = db.Column(db.String(25), nullable = False)
    total = db.Column(db.Integer, nullable = False)
    deliveryType = db.Column(db.String(30), nullable = False, default = 'COD')
    orderDate = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)
    
    def __repr__(self):
        return f"Post('{self.quantity}', '{self.color}', '{self.size}', '{self.status}', '{self.total}', '{self.deliveryType}', '{self.orderDate}')"


class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key = True)
    rate = db.Column(db.Integer, nullable = True)
    comments = db.Column(db.Text, nullable = True)

    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)
    
    def __repr__(self):
        return f"Post('{self.rate}', '{self.comments}')"


class Attributes(db.Model):
    __tablename__ = 'attributes'
    id = db.Column(db.Integer, primary_key = True)
    color = db.Column(db.String(10), nullable = True)
    size = db.Column(db.String(10), nullable = True)

    def __repr__(self):
        return f"Post('{self.color}', '{self.size}')"


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text, nullable = False)
    slug = db.Column(db.Text, nullable = False, unique = True)
    parentCategory = db.Column(db.Text, nullable = False, default = 'None')
    description = db.Column(db.Text, nullable = True)
    imageFile = db.Column(db.Text, nullable = False, default = 'category.jpg')

    def __repr__(self):
        return f"Post('{self.name}', '{self.parentCategory}', '{self.description}', '{self.imageFile}')"


class Brand(db.Model):
    __tablename__ = 'brand'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text, nullable = False)
    slug = db.Column(db.Text, nullable = False, unique = True)
    description = db.Column(db.Text, nullable = True)
    imageFile = db.Column(db.Text, nullable = False, default = 'Brand.jpg')

    def __repr__(self):
        return f"Post('{self.name}', '{self.description}', '{self.imageFile}')"


