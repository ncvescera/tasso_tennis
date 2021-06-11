from flask import request
from flask_json import as_json
from flask_login import login_required, current_user
from app import app, db, bcrypt, login_manager
from models import *
import json
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/api/fields', methods=['GET'])
def get_all_fields():
    if current_user.is_authenticated:
        if current_user.landowner:
            user_id = current_user.id

            dati = Field.query.filter_by(landowner_id=user_id)                    # prende tutti i campi
            dati_json = [x.as_dict() for x in dati]     # converte il risultato in dizionario per poter essere inviato a JS

            return json.dumps({'rep': dati_json}), 200

    return json.dumps({'error': 'Login first !'}), 401


@app.route('/api/fields', methods=['POST'])
@login_required
def add_field():
    if current_user.is_authenticated and current_user.landowner:    
        user_id = current_user.id

        name        = request.form['name']
        description = request.form['description']
        address = request.form['address']
        available_from = datetime.strptime(request.form['available_from'], '%H:%M').time()
        available_to = datetime.strptime(request.form['available_to'], '%H:%M').time()
        price_h = request.form['price_h']

        new_field = Field(
            name=name, 
            description=description, 
            address=address, 
            available_from=available_from, 
            available_to=available_to,
            price_h=price_h,
            landowner_id=user_id
            )

        try:
            db.session.add(new_field)
            db.session.commit()
        except:
            return json.dumps({'error': 'Esiste gia\' un campo con questo nome !'}), 400

        return json.dumps({'message': f'Campo {name} aggiunto con successo !'}), 200

    return json.dumps({'error': 'Login first !'}), 401


@app.route('/api/fields/<int:id>', methods=['DELETE'])
@login_required
def delete_field(id):
    if current_user.is_authenticated and current_user.landowner:    
        user_id = current_user.id

        to_delete = Field.query.filter_by(id=id, landowner_id=user_id).first()
        if to_delete:
            name = to_delete.name
            db.session.delete(to_delete)
            db.session.commit()

            return json.dumps({'message': f'Campo {name} eliminato con successo !'}), 200

        return json.dumps({'error': 'Campo inesistente !'}), 400

    return json.dumps({'error': 'Login first !'}), 401

    