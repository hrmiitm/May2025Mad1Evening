from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    isBlacklisted = db.Column(db.Boolean, default=False)

    isUser = db.Column(db.Boolean, default=True)
    isCreator = db.Column(db.Boolean, default=False)
    isAdmin = db.Column(db.Boolean, default=False)

    # songObj.user_id = 5
    # songObj.user = <u>   # user

    # userObj.songs ===> [<songObj1>, songObj2, ...]
    songs = db.relationship('Song', backref='user', lazy=True)  






    albums = db.relationship('Album', backref='user', lazy=True)

    # db.relationship ==> user-playlist one to many relationship
    playlists = db.relationship('Playlist', backref='user', lazy=True)
    # userObj.playlists = [<p1>, <p2>,....]
    # Incorrect --> userObj.user, userObj.Playlist



#2) new secondary table creation for many to many
SongInAlbum = db.Table('song_in_album',
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True),
    db.Column('album_id', db.Integer, db.ForeignKey('album.id'), primary_key=True)
)


SongInPlaylist = db.Table('song_in_playlist',
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True),
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
)


# songObj.user_id = 5
# songObj.user = <u>   # user

# userObj.songs = [<s1>, .....] # songs
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    lyrics = db.Column(db.String, default='')
    duration = db.Column(db.String, default='')
    date = db.Column(db.String, default='')
    rating = db.Column(db.Integer, default=0)

    isBlacklisted = db.Column(db.Boolean, default=False)


    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)







    # song-album ==> many to many
    #1) one line of code
    albums = db.relationship('Album', secondary=SongInAlbum, lazy='subquery', backref=db.backref('songs', lazy=True))

    # Song--Playlist many to many
    playlists = db.relationship('Playlist', secondary=SongInPlaylist, lazy='subquery', backref=db.backref('songs', lazy=True))
    # songObj.playlists ==> return [<p1>, <p2>, ...]


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)

    # for user-playlist ==> one to many relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, default='')
    artist = db.Column(db.String, default='')

    isBlacklisted = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class UserRating(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)
    rating = db.Column(db.Integer, unique=False)