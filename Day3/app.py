from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, User, Song
import os
from functools import wraps

app = Flask(__name__)


# Database
'''
1) Config
2) db from models. ==> SQLALCHEMY
'''
# _______Database Creation/connenction______
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'asdlfh'


# Connection to db
db.init_app(app)
app.app_context().push()
db.create_all() # update / create database schema
#__________________________________


def get_current_user(): # none or return object on user == one row of user table
    id = session.get('id', None)

    if id:
        u = User.query.filter_by(id=id).first()
        return u
    return None



#Function
def isUser(): # true or false
    return True if get_current_user() != None else False

def isCreator():
    u = get_current_user()
    if u and u.isCreator: return True
    return False

def isAdmin():
    u = get_current_user()
    if u and u.isAdmin: return True
    return False

#Decorator
def user_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            
            curr_id = session.get('id', None) # none, integer
            curr_user_obj = User.query.filter_by(id=curr_id).first()

            # login
            if curr_user_obj:
                return fn(*args, **kwargs)
            else:
                flash('You are not LoggedIn!', 'danger')
                return redirect(url_for('access'))

        return decorator

    return wrapper

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            curr_id = session.get('id', None)
            curr_user_obj = User.query.filter_by(id=curr_id).first()

            # login
            if curr_user_obj and curr_user_obj.isAdmin:
                return fn(*args, **kwargs)
            else:
                flash('You are not Admin!', 'danger')
                return redirect(url_for('access'))

        return decorator

    return wrapper

def creator_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            curr_id = session.get('id', None)
            curr_user_obj = User.query.filter_by(id=curr_id).first()

            # login and admin
            if curr_user_obj and curr_user_obj.isCreator:
                return fn(*args, **kwargs)
            else:
                flash('You are not Creator!', 'danger')
                return redirect(url_for('access'))

        return decorator

    return wrapper
















@app.route('/')
@user_required()
def home():
    user = get_current_user()
    name, email = (None, None)
    if user:
        name = user.name
        email = user.password


    return render_template("home.html", name=name, email=email, user=user)

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
        flash('Loggein Successfull', 'success')
        return redirect(url_for('home')) # home page
    flash('Either email or password incorrect', 'danger')
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
        flash("Regstraion Failed", 'danger')     
        return redirect(url_for('access'))
    if n == '' or e == '' or p == '':
        flash("Regstraion Failed", 'danger')
        return redirect(url_for('access'))
    
    if User.query.filter_by(email = e).first():
        flash("Regstraion Failed, user already exit", 'danger')
        return redirect(url_for('access'))
    

    # Create a New Row in User Table
    u = User(name=n, email=e, password=p) # Object == Row
    db.session.add(u)
    db.session.commit()

    flash('You got registered Please log in ', 'success')
    return redirect(url_for('access'))

@app.route("/logout")
def logout():
    session.pop('id', None)
    flash("Log Out Succesfull", 'success')
    return redirect(url_for('access'))

# url_for(home) ===> "/" == route value
# redirect("/") ====> it will go to route "/"


# NewPage songs, playlist
@app.route('/playlists')
@user_required()
def playlists():
    return 'soonn'

# /songs
# /songs?song_id=2
@app.route('/songs')
@creator_required()
def songs():
    user = get_current_user()
    songs = user.songs

    song_id = request.args.get('song_id')
    songobj = None
    if song_id:
        songobj = Song.query.filter_by(id = song_id).first()
    return render_template('songs.html', songs=songs, user=user, song=songobj)

@app.route('/upload_song', methods=['POST'])
@creator_required()
def upload_song():
    user = get_current_user()
    # get info
    name = request.form.get('name')
    lyrics = request.form.get('lyrics')
    duration = request.form.get('duration')
    date = request.form.get('date')

    file = request.files.get('songfile')

    # do data validation, (backend validation)
    if not file or not name:
        flash('Song file and name has to be provided!', 'danger')
        return redirect(url_for('songs'))

    # add to database song table ==> a row ==> a object
    songobj = Song(name=name, lyrics=lyrics, duration=duration, date=date, user_id=user.id)
    db.session.add(songobj)
    db.session.commit()

    # save .mp3 locally
    filename = f"{songobj.id}.mp3"
    # file.save(f'./staic/songs/{filename}')
    file.save(os.path.join('./static/songs/', filename))

    flash('Song Uploaded Successfully', 'success')
    return redirect(url_for('songs'))

@app.route('/update_song')
@creator_required()
def update_song():
    song_id = request.args.get('song_id')
    song = Song.query.filter_by(id = song_id).first()
    return render_template('update_song.html', song = song)

@app.route('/update_song_details', methods=['POST'])
@creator_required()
def update_song_details():
    user = get_current_user()
    song_id = request.args.get('song_id')

    # update to database song table ==> a row ==> a object
    songobj = Song.query.filter_by(id = song_id).first()
    songobj.name = request.form.get('name')
    songobj.lyrics = request.form.get('lyrics')
    songobj.duration = request.form.get('duration')
    songobj.date = request.form.get('date')
    db.session.commit()

    flash('Song Updated', 'success')
    return redirect(url_for('songs'))



# {{url_for('delete_song', song_id=song.id)}}
@app.route('/delete_song')
@creator_required()
def delete_song():
    # get the id of song
    song_id = request.args.get('song_id')

    # song object
    songobj = Song.query.filter_by(id = song_id).first()

    # delete song
    db.session.delete(songobj)
    db.session.commit()

    # song file also
    os.remove(f'./static/songs/{song_id}.mp3')

    flash('Song Deleted Successfully', 'success')
    return redirect(url_for('songs'))


if __name__ == "__main__":
    app.run(debug=True)