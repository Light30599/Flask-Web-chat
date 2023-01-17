from flask import Blueprint, render_template, request, flash, jsonify,redirect,url_for
from flask_login import login_required, current_user
from .models import Note,User,Room
from . import db
import json
from .encryption_decryption import rsa_encrypt_decrypt_key_generateur,rsa_encrypt,rsa_decrypt

views = Blueprint('views', __name__)


@views.route('/loading', methods=['GET'])
def loading():
    return render_template("loading-page.html")

@views.route('/action', methods=['GET'])
def action():
    import time
    time.sleep(5)
    return jsonify("oh so slow")

@views.route('/room_manager', methods=['GET'])
@login_required
def room_manager():
    return render_template("room_manager.html",user=current_user)

@views.route('/add_room', methods=['GET'])
@login_required
def add_room():
    if request.method == 'GET':
        import secrets
        uuid = secrets.token_hex(16)
        
        room = Room.query.filter_by(code=uuid).first()
        if room:
            flash('code error,try again later.', category='error')
        else:
            private_key,public_key = rsa_encrypt_decrypt_key_generateur()
            new_room = Room(code=uuid,state=True,author=current_user.id,prvkey=private_key,pubkey=public_key)
            db.session.add(new_room)
            db.session.commit()
            flash('Room created!', category='success')
            return redirect(url_for('views.loading',url="/"+uuid))

@views.route('/join_room', methods=['POST'])
@login_required
def join_room():
    if request.method == 'POST':
        code = request.form.get('code')

        room = Room.query.filter_by(code=code).first()
        if room:
            if room.state == True:
                flash('Room access successfully!', category='success')
                return redirect(url_for('views.loading',url="/"+code))
            else:
                flash('room inactive, try again.', category='error')
        else:
            flash('Room does not exist.', category='error')
    return redirect(url_for('views.room_manager'))

@views.route('/',defaults={'code': None}, methods=['GET', 'POST'])
@views.route('/<code>', methods=['GET', 'POST'])
@login_required
def home(code):
    if(code):
        room = Room.query.filter_by(code=code).first()
        if room:
            if room.state == True:
                flash('Room access successfully!', category='success')
            else:
                flash('room inactive, try again.', category='error')
                return redirect(url_for('views.room_manager'))
        else:
            flash('Room does not exist.', category='error')
            return redirect(url_for('views.room_manager'))
    else:
        flash('Choose a room please!', category='error')
        return redirect(url_for('views.room_manager'))

    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            encrypted_note = rsa_encrypt(note,room.pubkey)
            new_note = Note(data=encrypted_note, user_id=current_user.id,room_id=room.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    note_list = []
    for note in Note.query.filter_by(room_id=room.id).limit(10).all():
        #print(note.data)
        note.data = rsa_decrypt(note.data,room.prvkey).decode()
        note.user_id = User.query.filter_by(id=note.user_id).first().first_name
        note_list.append(note)
    #return render_template("home.html", user=current_user)
    return render_template("home.html", user=current_user,notes=note_list)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
