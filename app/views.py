import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm
from werkzeug.security import check_password_hash
from flask import send_from_directory

### 
# Routing for your application.
### 

# Set the upload folder configuration
app.config['UPLOAD_FOLDER'] = 'uploads'  # Ensure this matches your actual folder name

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required  # Ensures the route is only accessible to logged-in users
def upload():
    form = UploadForm()

    # If the form is submitted and validated
    if form.validate_on_submit():
        file = form.file.data  # Get the uploaded file

        if file:
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Flash a success message
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to the home page or another route

    return render_template('upload.html', form=form)  # Render the upload page with the form


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # If the form is submitted and validated
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query the database to find the user by username
        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()

        # If the user is found and the password matches
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful! Redirecting to the upload page...', 'success')
            return redirect(url_for('upload'))  # Redirect to the /upload route after successful login

        # If login fails, flash an error message
        flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html', form=form)


# User loader callback function
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()


###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send a static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to force the latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


def get_uploaded_images():
    upload_folder = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    image_files = []  # List to store image filenames

    # Walk through the folder and add image filenames to the list
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            # Check if file is an image (optional filtering)
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(file)

    return image_files


@app.route('/uploads/<filename>')
def get_image(filename):
    # Return the image file from the uploads folder
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)


@app.route('/files')
@login_required  # Ensure the user is logged in to access this page
def files():
    # Get the list of uploaded image filenames
    images = get_uploaded_images()
    return render_template('files.html', images=images)

