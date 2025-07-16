from flask import Flask, request, render_template, redirect, url_for, session, flash
from models import db, User, Song, Album, Playlist, UserRating
import os
from functools import wraps

from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
# 5abc ---> gph('5abc') ---> 'pbkdf2:sha256:260000$...$...'
# 5abc, 'pbkdf2:sha ---> cph(pbkdf2, '5abc') ---> true/false

app = Flask(__name__) # Object of Flask class

# For Database 
'''
1) Config --> uri
2) db = SQLAlchemy() ---> Getting from models
3) app and db setup
'''

# __________Database_____________
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'asdsd'  # Required for session management

# Connect to the database & make in context & create the database
db.init_app(app)
app.app_context().push()
db.create_all() # create or update the database schema
# __________Database End_____________



# Restful API
#______________DAY7 Restful Api________________________________________
from flask_restful import Api
api = Api(app) # setup



from myapi import GetDeleteSong, BlacklistSong, WhitelistSong

api.add_resource(GetDeleteSong, '/api/admin/get_delete_songs')
api.add_resource(BlacklistSong, '/api/admin/blacklist_song')
api.add_resource(WhitelistSong, '/api/admin/whitelist_song')

#_________________










# RBAC
#Function
def isUser(): # return true/false
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
            
            curr_id = session.get('id', None)
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

            # login and admin
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

            # login and creator
            if curr_user_obj and curr_user_obj.isCreator:
                return fn(*args, **kwargs)
            else:
                flash('You are not Creator!', 'danger')
                return redirect(url_for('access'))

        return decorator

    return wrapper

#_________
def get_current_user():
    id = session.get('id', None)  # return None or 4
    if id:
        return User.query.get(id)  # return <user1> == whole row
    return None



@app.route('/access')
def access():
    return render_template('access.html')

@app.route('/login', methods=['POST'])
def login():

    email = request.form.get('email')
    password = request.form.get('password')

    # u = User.query.filter_by(email=email, password=password) # [..,..,..]
    u = User.query.filter_by(email=email).first() # <user1>

    # from database it will search that email and password
    print(cph(u.password, password))
    if u and u.email==email and cph(u.password, password):
        session['id'] = u.id # Login
        if u.isAdmin:
            return redirect(url_for('admin_dashboard'))


        flash('Login Successfull', 'success')
        return redirect(url_for('home')) # Return to Home Page
   
    return redirect(url_for('access')) # return to access page again


@app.route('/register', methods=['POST'])
def register():
    # Get Data
    name = request.form.get('name')
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    img = request.files.get('image')

    if not(len(password1) == len(password2) and len(password1)<=10):
        flash('Max Password Lenght  should be 10 charater', 'danger')
        return redirect(url_for('access'))


    # Validate the data
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('User Already Exist', 'danger')
        return redirect(url_for('access'))

    # Check if passwords match
    if password1 != password2:
        flash('Password Do not Matched', 'danger')
        return redirect(url_for('access'))

    # Create new user
    new_user = User(name=name, email=email, password=gph(password1))
    db.session.add(new_user)
    db.session.commit()

    # save image in local storage
    filename=f'{new_user.id}.jpg'
    img.save(os.path.join('./static/profilePics/', filename))

    flash('User Created. Please Login Now', 'success')
    return redirect(url_for('access'))

@app.route('/logout')
def logout():
    session.pop('id', None)
    flash('Logout Successfull', 'success')
    return redirect(url_for('access'))  # Redirect to access page after logout


# Playlist
@app.route('/adsfhadsf')
@user_required()
def playlist():
    return "We will soon make it"

# Song Page

@app.route('/songs')
@creator_required()
def songs():
    user = get_current_user()
    songs = user.songs
    albums = user.albums
    
    song = None
    song_id = request.args.get('id')
    if song_id:
        song = Song.query.filter_by(id=song_id).first()
    

    return render_template('songs.html', curr_user=user, songs=songs, song=song, albums=albums)

@app.route('/upload_song', methods=['POST'])
@creator_required()
def upload_song():
    user = get_current_user()
    if user.isBlacklisted == True:
        flash("You are blacklisted by admin!! Not Allowed any upload", 'danger')
        return redirect(url_for('songs'))

    # get song data
    name = request.form.get('name')
    lyrics = request.form.get('lyrics')
    duration = request.form.get('duration')
    date = request.form.get('date')

    file = request.files.get('file')

    # Validation
    if not file or not name:
        flash('FileName and file need to be provided', 'danger')
        return redirect(url_for('songs'))

    # save info in db
    songobj = Song(name=name, lyrics=lyrics, duration=duration, date=date, user_id=user.id)
    db.session.add(songobj)
    db.session.commit()

    # save songfile in local storage
    filename=f'{songobj.id}.mp3'
    file.save(os.path.join('./static/songs/', filename))
    # file.save(f'./static/songs/{filename}')

    flash('Song Created Successfully', 'success')
    return redirect(url_for('songs'))


@app.route('/update_song')
@creator_required()
def update_song():
    song_id = request.args.get('song_id')
    songobj = Song.query.filter_by(id=song_id).first()
    return render_template('update_song.html', song=songobj)

@app.route('/update_song_details', methods=['POST'])
@creator_required()
def update_song_details():
    # get song data
    song_id = request.args.get('song_id')
    name = request.form.get('name')
    lyrics = request.form.get('lyrics')
    duration = request.form.get('duration')
    date = request.form.get('date')

    # update info in db
    songobj = Song.query.filter_by(id=song_id).first()
    songobj.name= name
    songobj.duration= duration
    songobj.lyrics= lyrics
    songobj.date= date
    db.session.commit()

    flash('Song Updated Successfully', 'success')
    return redirect(url_for('songs'))


@app.route('/delete_song')
@creator_required()
def delete_song():
    song_id = request.args.get('song_id')

    user = get_current_user()

    songobj = Song.query.filter_by (id = song_id).first()

    if not (songobj.user_id == user.id):
        flash('You are not creator of this Song', 'danger')
        return redirect(url_for('songs'))


    db.session.delete(songobj)
    db.session.commit()

    os.remove(f'./static/songs/{song_id}.mp3')
    flash('Song deleted Successfully', 'success')
    return redirect(url_for('songs'))


#_______________ALBUM____________________________________________________
@app.route('/albums')
def albums():
    curr_user = get_current_user()         
    albums = curr_user.albums

    return render_template('albums.html', curr_user=curr_user, albums=albums)

@app.route('/upload_album', methods=["POST"])
def upload_album():
    curr_user = get_current_user()         
    print(request.form) # [('name', ''), ('genre', ''), ('artist', '')]
    print(request.files)  #[('files', <FileStorage: 'Dope Shope - Yo Yo Honey Singh33309.m4a' ('audio/x-m4a')>), ('files', <FileStorage: 'Ishare Tere - Guru Randhawa, Dhvani Bhanushali13.m4a' ('audio/x-m4a')>)]

    # get form data
    name = request.form.get('name')
    genre = request.form.get('genre')
    artist = request.form.get('artist')

    files = request.files.getlist('files')

    # error parts
    if not name or not files:
        flash('Name and File Required', 'danger')
        return redirect(url_for('albums'))
    if len(files) == 1 and files[0].filename == '':
        flash('File Required', 'danger')
        return redirect(url_for('albums'))
    

    albumObj = Album(name=name, genre=genre, artist=artist, user_id=curr_user.id)
    db.session.add(albumObj)
    db.session.commit()
    album_id = albumObj.id

    for file in files:
        # entry in database > in song table
        songObj = Song(name=file.filename, user_id=curr_user.id)
        db.session.add(songObj)
        db.session.commit()
        song_id = songObj.id

        # entry in staic file .mp3 saving
        filename = f"{song_id}.mp3"
        file.save(os.path.join('./static/songs', filename))
        

        # entry in > album
        albumObj.songs.append(songObj)
        db.session.commit()


    flash('Album Uploaded Successfully', 'success')
    return redirect(url_for('albums'))


@app.route('/add_to_album/<int:song_id>/<int:album_id>')
def add_to_album(song_id, album_id):
    curr_user = get_current_user()         
    songObj = Song.query.filter_by(id=song_id).first()
    albumObj = Album.query.filter_by(id=album_id).first()
   
    
    albumObj.songs.append(songObj)
    db.session.commit()
    flash('Song Added To Album Successfully', 'success')
    return redirect(url_for('songs'))

@app.route('/delete_album')
def delete_album():
    curr_user = get_current_user()         

    album_id = request.args.get('id')

    album = Album.query.filter_by(id=album_id).first() # fetch row
    allsongs = album.songs
    while allsongs != []:
        song = allsongs.pop()
        song.albums = []
        song.playlists = []
        db.session.commit()

        # delete file | From static/songs/id.mp3
        print(f'{song.id}')
        os.remove(f'./static/songs/{song.id}.mp3')

        db.session.delete(song)
        db.session.commit()
        
    name = album.name
    db.session.delete(album) # delete
    db.session.commit()         # commit

    flash(f'Album {name} Deleted Successfully', 'success')
    return redirect(url_for('albums'))

@app.route('/removeFromAlbum')
def remove_from_album():
    curr_user = get_current_user()         

    album_id = request.args.get('album_id')
    song_id = request.args.get('song_id')

    album = Album.query.filter_by(id=album_id).first()
    song = Song.query.filter_by(id=song_id).first()
    album.songs.remove(song)
    db.session.commit()

    return redirect(url_for('albums'))

# ___________________________________Album PAGE DONE_____________________

#Profile

@app.route('/profile')
@user_required()
def profile():
    userObj = get_current_user() #<u>  # curr logged in user
    statsDict = {
        'Songs': None,
        'Albums': None
    }
    if userObj.isCreator:
        statsDict['Songs'] = len(userObj.songs)
        statsDict['Albums'] = len(userObj.albums)
    return render_template('profile.html', curr_user = userObj, creator_stats= statsDict)


@app.route('/update_profile', methods=['POST'])
@user_required()
def update_profile():
    # get data
    e = request.form.get('email')
    p = request.form.get('password')
    old_password = request.form.get('old_password')
    pic = request.files.get('pic')

    # update data
    curr_user = get_current_user()
    if p != '' and curr_user.password != old_password:
        flash('Incorrect Old Password', 'danger')
        return redirect(url_for('profile'))
    
    if e != '':
        curr_user.email = e
        flash('Email Updated', 'success')
    if p != '':
        curr_user.password = p
        flash('Password Update', 'success')
    db.session.commit()

    if pic:
        name = f"{curr_user.id}.jpg"
        pic.save(f'./static/profilePics/{name}')
        flash('Profile Picture Update', 'success')

    return redirect(url_for('profile'))


# Role Upgrade. User.isCreator = false to making True
@app.route('/becomeCreator')
@user_required()
def becomeCreator():
    curr_user = get_current_user()
    curr_user.isCreator = True
    db.session.commit()

    flash('You are Creator Now', 'success')
    return redirect(url_for('profile'))

#____________Profile Page Done________________

# _______________Playlist Home Page_______________________
@app.route('/')
@user_required()
def home():
    curr_user = get_current_user()
    if curr_user == None:
        flash("Please Login First", 'danger')
        return redirect(url_for('login'))
    # filterby ==> taking only whitelisted
    songs = Song.query.filter_by(isBlacklisted=False).order_by(Song.rating.desc())


    playlists = curr_user.playlists # [<P1>, ....], P1.SONGS = <s1>...

    #if user hit /?song_id=5
    song_id = request.args.get('song_id')
    if song_id: song=Song.query.filter_by(id=song_id).first()
    else: song=None

    #if user hit /?search=Worl
    search = request.args.get('search')  # None, "leoabc"
    if search:
        songs = Song.query.filter_by(isBlacklisted=False).filter(Song.name.contains(search)).all()

    return render_template('home.html', curr_user = get_current_user(), songs=songs, playlists=playlists, song=song, search=search)

#Rating
@app.route('/rating', methods=['POST'])
@user_required()
def rating():
    curr_user = get_current_user()    

    user_id = curr_user.id
    song_id = request.args.get('song_id') # song_id in url_for 
    rating = request.form.get('rating') # Name of input in Form

    # Update/CreateNew ---> UserRating Table ---> (user_id, song_id, Rating)
    ur = UserRating.query.filter_by(user_id=user_id, song_id=song_id).first()
    if not ur:
        ur = UserRating(user_id=user_id, song_id=song_id, rating=rating)
        db.session.add(ur)
        db.session.commit()
    else:
        ur.rating = rating
        db.session.commit()


    # Update ---> Song Table ------> (id, ...., ...., .... Rating=AvgValue)
    all_ur = UserRating.query.filter_by(song_id=song_id).all() # [<ur>,.....]
    list_rating = [int(ur.rating) for ur in all_ur]
    avg_rating = sum(list_rating)/len(list_rating)

    # s = 0
    # n = 0
    # for ur in all_ur:
    #     r = ur.rating
    #     s += r
    #     n += 1
    song = Song.query.filter_by(id = song_id).first()
    song.rating = avg_rating
    db.session.commit()



    flash(f'Rating Added to Song : {song.name}', 'success')
    return redirect(url_for('home'))

# Playlist Views
@app.route('/playlists')
def playlists():
    curr_user = get_current_user()         
    playlists = curr_user.playlists

    song_id=request.args.get('song_id')
    song=None
    if song_id:
        song = Song.query.filter_by(id=song_id).first()

    return render_template('playlists.html', curr_user=curr_user, playlists=playlists, song=song)

# Four Operation on views
# AND return(redirect(url_for('playlists')))
'''
1) Create Playlist
    INPUT ===> Name, User_id  
          ===> form/args, session/login/get_currentUsre().id

    Operation == > p Playlist(nam = sad) , add, commit


2) Add Song In Playlist
    INPUT ==> SongId, PlaylistId, User_id
          ==> args/form             session/login/get_currentUser.id



3) Delete The Playlist
    INPUT ==> PlyalistId
        ==> args/form


4) Remove a song from playlist
    INPUT ==> SONGID, PLAYLISTID



'''
@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    curr_user = get_current_user()         
    name = request.form.get('name')

    playlistObj = Playlist(name=name, user_id=curr_user.id)
    db.session.add(playlistObj)
    db.session.commit()

    flash('Playlist Created Successfully', 'success')
    return redirect(url_for('playlists'))

# add_to_playlist?playlist_id=1&song_id=4
@app.route('/add_to_playlist')
def add_to_playlist():
    curr_user = get_current_user()        
    #id
    playlist_id = request.args.get('playlist_id')
    song_id = request.args.get('song_id')

    #obj
    playlist = Playlist.query.filter_by(id=playlist_id).first() # <p1>
    song = Song.query.filter_by(id=song_id).first() # <s2>

    # simple list append
    playlist.songs.append(song)
    db.session.commit()

    flash("Song Added to Playlist", "success")
    return redirect(url_for('home'))

@app.route('/delete_playlist')
def delete_playlist():
    curr_user = get_current_user()         

    id = request.args.get('id')

    playlist = Playlist.query.filter_by(id=id).first() # fetch row
    playlist.songs = []
    
    name = playlist.name
    db.session.delete(playlist) # delete
    db.session.commit()         # commit

    flash(f'Playlist {name} Deleted Successfully', 'success')
    return redirect(url_for('playlists'))

@app.route('/removeFromPlaylist')
def remove_from_playlist():
    curr_user = get_current_user()         

    #get Id
    playlist_id = request.args.get('playlist_id')
    song_id = request.args.get('song_id')

    #get Obj/row
    playlist = Playlist.query.filter_by(id=playlist_id).first()
    song = Song.query.filter_by(id=song_id).first()

    playlist.songs.remove(song)
    db.session.commit()
    print('hello')
    return redirect(url_for('playlists'))


#___________________________ADMIN DASHBOARD_________________________
def create_graphs():
    from models import User, Song
    import matplotlib
    matplotlib.use('Agg') # important line

    import matplotlib.pyplot as plt
    plt.figure(figsize=(2,2))



    ad = User.query.filter_by(isAdmin=True).count() #no. of admin
    cr = User.query.filter_by(isCreator=True).count()
    us = User.query.filter_by(isAdmin=False, isCreator=False).count()


    x = ['User', 'Creators', 'Admin']
    y = [us, cr, ad]

    plt.bar(x, y)
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha = 'center', va = 'bottom')
    plt.savefig('./static/bar.jpg')
    plt.close()

    b_s = Song.query.filter_by(isBlacklisted=True).count()
    w_s = Song.query.filter_by(isBlacklisted=False).count()
    y = [w_s, b_s] # ttotal = b_s + w_s;       angel = b_s/0;

    if b_s and w_s:
      x = ['Whitelisted Songs', 'Blacklisted Songs']
      plt.pie(y, labels=x, autopct='%1.1f%%')
    plt.savefig('./static/pie.jpg')
    plt.close()

# /admin/dashboard
# /admin/dashboard?song_id=2
@app.route('/admin/dashboard')
def admin_dashboard():
    curr_user = get_current_user()         

    # Row1
    create_graphs() # create new bar.png in static folder
    
    # /admin/dashboard?song_id=1
    song_id = request.args.get('song_id')
    song = None
    if song_id:
        song = Song.query.filter_by(id=song_id).first()  # donot forget first()

    # Row2
    white_songs = Song.query.filter_by(isBlacklisted=False).all() # [<ws1> ,<ws2>,.....]
    black_songs = Song.query.filter_by(isBlacklisted=True).all() # [<ws1> ,<ws2>,.....]

    # Row3
    white_creators = User.query.filter_by(isBlacklisted=False, isCreator=True).all() # [<wu1> ,<ws2>,.....]
    black_creators = User.query.filter_by(isBlacklisted=True, isCreator=True).all() # [<wu1> ,<ws2>,.....]
    

    return render_template('admin_dashboard.html', white_songs=white_songs, black_songs=black_songs,  white_creators=white_creators, black_creators=black_creators, song=song)


#______________DELETE SONG BY ADMIN_____________________
# /admin/deleteSong?song_id=6
@app.route('/admin/deleteSong')
def admin_delete_song():
    song_id = request.args.get('song_id') ## 100
    if song_id:
        song = Song.query.filter_by(id=song_id).first() #songObj ==> one row inDBtable.Song
        if song:
            os.remove(f'./static/songs/{song.id}.mp3') # deletion of file
            db.session.delete(song)                    # deletion from database
            db.session.commit()
            flash('Song Deleted Succefully!', 'success')
        else:
            flash('Invalid Id', 'danger')
    else:
        flash('SongId Not Provided', 'danger')
    
    return redirect(url_for('admin_dashboard'))


#_______________BLACKLIST/WHITELIST SONG BY ADMIN_______
@app.route('/admin/blacklistSong')
def admin_blacklist_song():
    song_id = request.args.get('song_id') # 8
    song = Song.query.filter_by(id=song_id).first() # None, <song 1>
    if song:
        song.isBlacklisted = True
        db.session.commit()
    flash('BlacklistedSuccessfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/whitelistSong')
def admin_whitelist_song():
    song_id = request.args.get('song_id')
    song = Song.query.filter_by(id=song_id).first()
    if song:
        song.isBlacklisted = False
        db.session.commit()
        flash('Whitelisted Successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


#_______________BLACLIST/WHITELIST CREATOR BY ADMIN_____
@app.route('/admin/blacklistCreator')
def admin_blacklist_creator():
    # /admin/blacklistCreator
    # /admin/blacklistCreator?creator_id=1

    # int id ==> userobj
    creator_id = request.args.get('creator_id')
    creator = User.query.filter_by(id=creator_id, isCreator=True).first()

    # userobj.isBlacklisted = True
    creator.isBlacklisted = True
    db.session.commit()

    flash('Blacklisted Creator Successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/whitelistCreator')
def admin_whitelist_creator():

    creator_id = request.args.get('creator_id')
    creator = User.query.filter_by(id=creator_id, isCreator=True).first()
    if creator:
        creator.isBlacklisted = False
        db.session.commit()
        flash('Whitelisted Creator Successfully!', 'success')
    return redirect(url_for('admin_dashboard'))






# _____________Profile And Home Page_______________________
if __name__ == '__main__':
    app.run(debug=True)

    # print(__name__) # __name__ if directly executed
# # if you import then that name would be not __main__