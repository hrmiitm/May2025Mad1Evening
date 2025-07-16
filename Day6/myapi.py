from flask import make_response, jsonify, request
from flask_restful import Resource
from models import db, User, Song
import os

def isAdmin(email, password):
    u = User.query.filter_by(email=email, password=password, isAdmin=True).first()
    if u:
        return True
    return False

def deleteSong(song_id):
    song = Song.query.filter_by(id=song_id).first()
    if song:
        song.albums = []
        song.playlists = []
        db.session.commit()

        db.session.delete(song)
        db.session.commit()

        path = f'./static/songs/{song.id}.mp3'
        os.remove(path)
        return True
    return False

def getAllSongsDetails():
    whitesongs = Song.query.filter_by(isBlacklisted=False).all() # [<son>, <son>...]
    blacksongs = Song.query.filter_by(isBlacklisted=True).all()
    d = {}
    d['WhiteSongs'] = [{'id':song.id, 'name':song.name} for song in whitesongs]
    d['BlackSongs'] = [{'id':song.id, 'name':song.name} for song in blacksongs]
    return d


def blacklistSong(song_id):
    song = Song.query.filter_by(id=song_id).first()
    if song:
        song.isBlacklisted = True
        db.session.commit()
        return True
    return False
def whitelistSong(song_id):
    song = Song.query.filter_by(id=song_id).first()
    if song:
        song.isBlacklisted = False
        db.session.commit()
        return True
    return False


class GetDeleteSong(Resource):
    def get(self):
        email = request.json.get('email')
        password = request.json.get('password')

        if isAdmin(email, password):
            songs_details = getAllSongsDetails() # dictionary
            return make_response(jsonify(songs_details), 200)
        else:
            d = {'message': 'Access Denied!'}
            return make_response(jsonify(d), 403)

    def delete(self):

        email = request.json.get('email')
        password = request.json.get('password')
        song_id = request.json.get('song_id')
        
        if isAdmin(email, password) and song_id:
            if deleteSong(song_id):
                return make_response('Delete Song Succesful', 200)
            else:
                d = {'message': 'Song not found'}
                return make_response(jsonify(d), 400)

        else:
            d = {'message': 'Either you are not admin or song_id not provided'}
            return make_response(jsonify(d), 400)
        

class BlacklistSong(Resource):
    def get(self):
        email = request.json.get('email')
        password = request.json.get('password')
        song_id = request.json.get('song_id')

        if isAdmin(email, password):
            if blacklistSong(song_id):
                d = {'message': 'Song Blacklisted'}
            else:
                d = {'message': 'Song Not Found'}
            return make_response(jsonify(d), 200)
        else:
            d = {'message': 'Access Denied!'}
            return make_response(jsonify(d), 403)


class WhitelistSong(Resource):
    def get(self):
        email = request.json.get('email')
        password = request.json.get('password')
        song_id = request.json.get('song_id')

        if isAdmin(email, password):
            if whitelistSong(song_id):
                d = {'message': 'Song Whitelisted'}
            else:
                d = {'message': 'Song Not Found'}
            return make_response(jsonify(d), 200)
        else:
            d = {'message': 'Access Denied!'}
            return make_response(jsonify(d), 403)