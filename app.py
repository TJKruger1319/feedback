from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
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
    """Returns to the register route"""
    return redirect("/register")

@app.route("/register", methods=['GET', 'POST'])
def new_user():
    """Shows the register user form and then adds the user upon successful submit"""
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
        return redirect(f"/users/{username}")

    return render_template('register.html', form=form)

@app.route("/users/<username>")
def show_user(username):
    """Show the information about the user and their feedback"""
    if "user_username" not in session:
        flash("Please login first!")
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    feedback = Feedback.query.filter_by(username=username).all()
    return render_template("user.html", user=user, feedback=feedback)

@app.route("/login", methods=['GET', 'POST'])
def returning_user():
    """Allows for the user to login"""
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
    """Removes the user from the session"""
    if "user_username" in session:
        session.pop("user_username")
    return redirect("/")

@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    """Removes the user and their feedback from the database"""
    user = User.query.filter_by(username=username).first()
    feedback = Feedback.query.filter_by(username=username).all()
    for fb in feedback:
        db.session.delete(fb)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    session.pop("user_username")
    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def new_feedback(username):
    """Adds new feedback to the database"""
    if "user_username" not in session:
        flash("Please login first!")
        return redirect('/')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{username}")
    return render_template("feedback.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    """Edit feedback you've posted"""
    feedback = Feedback.query.get_or_404(feedback_id)
    try:
        if session['user_username'] != feedback.username:
            flash("You can only edit your own feedback.")
            return redirect("/")
    except KeyError:
        flash("Please login first!")
        return redirect("/")
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    return render_template("editfeedback.html", form=form)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback you've posted"""
    feedback = Feedback.query.get_or_404(feedback_id)
    try:
        if session['user_username'] != feedback.username:
            flash("You can only delete your own feedback.")
            return redirect("/")
    except KeyError:
        flash("Please login first!")
        return redirect("/")
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{feedback.username}")