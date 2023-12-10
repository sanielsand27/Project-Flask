from unicodedata import category
from hardware import app, allowed_file
from flask import Flask, render_template, redirect, url_for, flash, request, send_file, jsonify
from hardware.models import  Item, User, MyModel, License
from hardware.forms import RegisterForm, LoginForm, Form, Insert
from hardware import db
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import urllib.request
import os, json
from io import BytesIO
from flask_toastr import Toastr

toastr = Toastr(app)






#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


#def allowed_file(filename):
# return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/home')
@login_required
def home_page():
    data3 = db.session.query(User).count()
    return render_template('dashboard.html', data3=data3)

@app.route('/CompList')
def list_page():
    items = Item.query.all()
    #items.owner = User.query.filter_by(items).first().id
    return render_template('complist.html', items=items)

@app.route('/CompList2')
def list2_page():
    #items = Item.query.all()
    #items.owner = User.query.filter_by(items).first().id
    return render_template('complist2.html')

@app.route('/User_List')
def user_list_page():
    users = User.query.all()
    #items.owner = User.query.filter_by(items).first().id
    return render_template('user_list.html', users=users)





################## Registration ##################

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('home_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


################## Login ##################

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)



################## Logout ##################

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("login_page"))








@app.route('/profile')
def profile_page():
    users = User.query.all()
    #items.owner = User.query.filter_by(items).first().id
    return render_template('user_profile.html', users=users)

@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/asset')
def asset_page():
   return render_template('asset.html')

@app.route('/index')
def index_page():
   return render_template('index.html')


#@app.route('/comp')
#def comp_page():
#  form = Insert()
#     if form.validate_on_submit():
        
#        insert = Item(name=form.name.data, price=form.price.data, barcode=form.barcode.data, description=form.description.data, owned_user=current_user)
#        db.session.add(insert)
#        db.session.commit()
#        flash('Your post has been created!', 'success')
#        return redirect(url_for('home'))
#    return render_template('asset.html', title='New Post',
 #                          form=form, legend='New Post')


#@app.route('/add', methods=['GET', 'POST'])
#def index():
#    form = Insert()
   
#    if request.method == "POST":
#        file = request.files['inputFile']
#        filename = secure_filename(file.filename)

#    if file and allowed_file(file.filename):
#        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#        insert = Item(name=form.name.data, price=form.price.data, barcode=form.barcode.data, description=form.description.data, owned_user=current_user,filename=file.filename)
#        db.session.add(insert)
#        db.session.commit()
#        flash('Your post has been created!', 'success')
#        return redirect(url_for('home_page'))
#    return render_template('add.html', form=form)







@app.route("/post", methods=['GET', 'POST'])
def post():
    form = Insert()
    
    if form.validate_on_submit():
        
        insert = Item(name=form.name.data, price=form.price.data, barcode=form.barcode.data, description=form.description.data, owned_user=current_user)
        db.session.add(insert)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home_page'))
    return render_template('asset.html', title='New Post',
                           form=form, legend='New Post')


 #       name = request.form.get('name')
 #       price = request.form.get('price')
 #       barcode = request.form.get('barcode')
 #       desc = request.form.get('description')

 #   workout = Item(name=name, price=price, barcode=barcode, description=desc, owned_user=current_user)
 # db.session.add(workout)
 #   db.session.commit()

 #   flash('Your workout has been added!')

 #   return redirect(url_for('home_page'))







#@app.route('/profile')
#def profile_page():
#    users = User.query.all()
#    return render_template('user_profile.html', users=users)



@app.route('/license')
def license_page():
    options = License.query.all()
    return render_template('license.html', options=options)





@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form.get('inputName')
    date_str = request.form.get('inputDate')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    picture = request.files.get('inputPicture')
    filename = secure_filename(picture.filename)
    year_subscription = request.form.get('year_subscription')
    if year_subscription is None:
        year_subscription = 1
    else:
        year_subscription = int(year_subscription)
    expiration_date = date + relativedelta(years=+year_subscription)
    
    if picture and allowed_file(picture.filename):
        
        picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        picture_data = License(name=name, date=date, picture_path= filename, year_subscription=year_subscription, expiration_date = expiration_date)
        db.session.add(picture_data)
        db.session.commit()
 
        flash('Your post has been created!', 'success')
        return redirect(url_for('license_page'))
    else:
        flash('Your post was not created', 'error')
        return redirect(url_for('license_page'))


@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = License.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash('License Deleted Successfully!', 'success')
    return redirect(url_for('license_page'))


@app.route('/asset/<int:id>')
def asset(id):
    # fetch the asset data using the id
    asset = License.query.get(id)

    # render the asset_page template and pass the asset data to the template
    return render_template('asset.html', asset=asset)




############## CALENDAR #################

@app.route('/calendar')
def calendar():
    events = [
        {
            'title': 'Event 1',
            'start': '2023-02-15',
            'end': '2023-02-16'
        },
        {
            'title': 'Event 2',
            'start': '2023-02-17',
            'end': '2023-02-18'
        }
    ]
    return render_template('calendar.html', events=json.dumps(events))


