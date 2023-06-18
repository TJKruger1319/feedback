from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.app_context().push()

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route("/")
def redirect_to_register():
    return redirect("/register")

@app.route("/register", methods=['GET', 'POST'])
def new_user():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username has already been taken')
            return render_template("register.html", form=form)
        session['user_username'] = new_user.username
        flash('Successfully created user.')
        return redirect("/secret")

    return render_template('register.html', form=form)

@app.route("/users/<username>")
def show_user(username):
    if "user_username" not in session:
        flash("Please login first!")
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    return render_template("user.html", user=user)

@app.route("/login", methods=['GET', 'POST'])
def returning_user():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['user_username'] = user.username
            return redirect(f"/users/{username}")
        else:
            form.username.errors = ["Invalid username/password"]
    
    return render_template("login.html", form=form)

@app.route("/logout")
def logout_user():
    session.pop("user_username")
    return redirect("/")