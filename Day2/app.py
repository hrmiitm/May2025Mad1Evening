from flask import Flask, render_template, redirect, url_for, request, session
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'asdlfh'


# Connection to db
db.init_app(app)
app.app_context().push()
db.create_all() # update / create database schema


def get_current_user(): # none or return object on user == one row of user table
    id = session.get('id', None)

    if id:
        u = User.query.filter_by(id=id).first()
        return u
    return None


@app.route('/')
def home():
    user = get_current_user()
    name, email = (None, None)
    if user:
        name = user.name
        email = user.password


    return render_template("home.html", name=name, email=email)

@app.route('/access')
def access():
    return render_template("access.html")

@app.route('/login', methods=['POST'])
def login():
    # get the email/password
    e = request.form.get('email')
    p = request.form.get('password')

    # validate it and check both matched
    u = User.query.filter_by(email=e, password=p).first()

    if u:
        session['id'] = u.id # login
        return redirect(url_for('home')) # home page
    return redirect(url_for('access')) # access page

@app.route("/register", methods=['POST'])
def register():
    # Get Form Data
    n = request.form.get('name') # string, None
    e = request.form.get('email')
    p = request.form.get('password1')
    cp = request.form.get('password2')

    # Validate
    # e should not be already there
    # p == cp
    # n and e != ""
    if not(n and p and cp and p == cp):
        return redirect(url_for('access'))
    if n == '' or e == '' or p == '':
        return redirect(url_for('access'))
    
    if User.query.filter_by(email = e).first():
        return redirect(url_for('access'))
    

    # Create a New Row in User Table
    u = User(name=n, email=e, password=p) # Object == Row
    db.session.add(u)
    db.session.commit()

    return redirect(url_for('access'))


@app.route("/logout")
def logout():
    session.pop('id', None)
    return redirect(url_for('access'))

# url_for(home) ===> "/" == route value
# redirect("/") ====> it will go to route "/"

if __name__ == "__main__":
    app.run(debug=True)