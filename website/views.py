from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from . import db
from .models import Password, User
from .security import decrypt, encrypt, generatePassword
import pyperclip

views = Blueprint("views", __name__)

# Default screen is the login screen
@views.route("/", methods=["GET", "POST"])
def main():
    return redirect(url_for("views.login"))

@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "signup" in request.form:
            return redirect(url_for("views.signup"))
        
        # Make sure inputted username and password exists in the database, otherwise user needs to signup instead
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=encrypt(username)).first()
        if user:
            if encrypt(password) == user.password:
                flash("Login successful!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password", category="error")
        else:
            flash("Username does not exist", category="error")
        
    return render_template("login.html")

@views.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if "cancel" in request.form:
            return redirect(url_for("views.login"))
        
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        
        user = User.query.filter_by(username=encrypt(username)).first()
        if user:
            flash("That username already exists. Please select a different one.", category="error")
            return render_template("signup.html", username=username, password=password, password2=password2)
        elif len(password) < 20:
            flash("For security reasons, make sure your password is at least 20 characters.", category="error")
            return render_template("signup.html", username=username, password=password, password2=password2)
        elif password != password2:
            flash("Passwords did not match", category="error")
            return render_template("signup.html", username=username, password=password, password2=password2)
        else:
            new_user = User(username=encrypt(username), password=encrypt(password))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            login_user(new_user, remember=True)
            return redirect(url_for("views.home"))
    
    return render_template("signup.html", username="", password="", password2="")

# Home screen allows user to access the various other screens as well as copying passwords
@views.route("/home", methods=["GET", "POST"])
@login_required
def home():
    username = current_user.username
    if request.method == "POST":
        password_name = request.form.get("password-dropdown")
        password = Password.query.filter_by(username=username, password_name=password_name).first()
        
        if "logout" in request.form:
            logout_user()
            return redirect(url_for("views.login"))
        elif "edit-profile" in request.form:
            return redirect(url_for("views.edit_profile", new_username="", new_password="", new_password2=""))
        elif "add" in request.form:
            return redirect(url_for("views.add_password", password_name="", password_value="", show=0))
        elif "change" in request.form:
            return redirect(url_for("views.edit_password", password_name=password_name, password_value=decrypt(password.password_value), show=0))
        elif "delete" in request.form:
            db.session.delete(password)
            db.session.commit()
        elif "copy" in request.form:
            pyperclip.copy(decrypt(password.password_value))
            flash("Password has been copied to clipboard!")
    
    passwords = Password.query.filter_by(username=username).all()
    return render_template("home.html", username=decrypt(username), passwords=passwords)

# Edit profile screen allows user to change their username and master password
@views.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        new_username = request.form.get("new-username")
        new_password = request.form.get("new-password")
        new_password2 = request.form.get("new-password2")
        if "cancel" in request.form:
            return redirect(url_for("views.home"))
        elif "update" in request.form:
            if new_username != "":
                new_username = encrypt(new_username)
                
            if new_password == "":
                new_password = current_user.password
            elif new_password != new_password2:
                flash("Passwords don't match.", category="error")
                return render_template("edit_profile.html", new_username=decrypt(new_username), new_password=new_password, new_password2=new_password2)
            else:
                new_password = encrypt(new_password)
            
            if new_username != "" and new_username != current_user.username and User.query.filter_by(username=new_username).first():
                flash("That username already exists. Please select another one.", category="error")
                return render_template("edit_profile.html", new_username=decrypt(new_username), new_password=decrypt(new_password), new_password2=new_password2)
            
            if len(new_password) < 20:
                flash("For security reasons, make sure your password is at least 20 characters.", category="error")
                return render_template("edit_profile.html", new_username=decrypt(new_username), new_password=decrypt(new_password), new_password2=new_password2)
            
            if new_username != "":
                for password in Password.query.filter_by(username=current_user.username).all():
                    password.username = new_username
                    
                current_user.username = new_username
                
            current_user.password = new_password
        
            db.session.commit()
            flash("Profile has been updated successfully!", category="success")
        
        return redirect(url_for("views.home"))
    
    new_username = request.args.get("new_username")
    new_password = request.args.get("new_password")
    new_password2 = request.args.get("new_password2")
    return render_template("edit_profile.html", new_username=new_username, new_password=new_password, new_password2=new_password2)

# Screen for adding a new password for the user, with an option to auto-generate one for them.
@views.route("/add_password", methods=["GET", "POST"])
@login_required
def add_password():
    if request.method == "POST":
        password_name = request.form.get("password-name")
        password_value = request.form.get("password-value")
        if "cancel" in request.form:
            return redirect(url_for("views.home"))
        elif "show" in request.form:
            return render_template("add_password.html", password_name=password_name, password_value=password_value, show=1)
        elif "hide" in request.form:
            return render_template("add_password.html", password_name=password_name, password_value=password_value, show=0)
        elif "auto-generate" in request.form:
            new_value = generatePassword()
            return render_template("add_password.html", password_name=password_name, password_value=new_value, show=0)
        
        new_value = encrypt(password_value)
        new_password = Password(username=current_user.username, password_name=password_name, password_value=encrypt(new_value))
        db.session.add(new_password)
        db.session.commit()
        
        return redirect(url_for("views.home"))
    
    password_name = request.args.get("password_name")
    password_value = request.args.get("password_value")
    show = request.args.get("show")
    return render_template("add_password.html", password_name=password_name, password_value=password_value, show=show)

@views.route("/edit_password", methods=["GET", "POST"])
@login_required
def edit_password():
    if request.method == "POST":
        password_name = request.form.get("password-name")
        password_value = request.form.get("password-value")
        if "cancel" in request.form:
            return redirect(url_for("views.home"))
        elif "auto-generate" in request.form:
            new_value = generatePassword()
            return render_template("edit_password.html", password_name=password_name, password_value=new_value, show=0)
        elif "show" in request.form:
            return render_template("edit_password.html", password_name=password_name, password_value=password_value, show=1)
        elif "hide" in request.form:
            return render_template("edit_password.html", password_name=password_name, password_value=password_value, show=0)
        elif "update" in request.form:
            new_value = request.form.get("password-value")
            
            if new_value == "":
                flash("Please enter a new password.", category="error")
                return render_template("edit_password.html", password_name=password_name, password_value="", show=0)
            
            password = Password.query.filter_by(username=current_user.username, password_name=password_name).first()
            password.password_value = encrypt(new_value)
            db.session.commit()
        
        return redirect(url_for("views.home"))
    
    password_name = request.args.get("password_name")
    password_value = request.args.get("password_value")
    show = request.args.get("show")
    return render_template("edit_password.html", password_name=password_name, password_value=password_value, show=show)