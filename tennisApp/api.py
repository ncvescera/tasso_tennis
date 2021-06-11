from flask import request
from flask_json import as_json
from flask_login import login_required, current_user
from app import app, db, bcrypt, login_manager
from models import *
import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/api/fields', methods=['GET'])
def get_all_fields():
    if current_user.is_authenticated:
        user_id = current_user.id

        dati = Field.query.filter_by(landowner_id=user_id)                    # prende tutti i campi
        dati_json = [x.to_dict() for x in dati]     # converte il risultato in dizionario per poter essere inviato a JS

        return json.dumps({'rep': dati_json}), 200

    return json.dumps({'error': 'Login first !'}), 401

@app.route('/api/fields', methods=['POST'])
@as_json
@login_required
def add_field():
    print('aaaaaaaaaaaaaaaaa')
    print(current_user.is_authenticated)
    if current_user.is_authenticated:
        print('bbb')
        data = request.json
    
        user_id = current_user.id

        name        = data['name']
        description = data['description']
        address = data['address']
        available_from = data['available_from']
        available_to = data['available_to']
        price_h = data['price_h']

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
            return {'error': 'Esiste gia\' un campo con questo nome !'}, 400

        return {'message': f'Campo {nome} aggiunto con successo !'}, 200

    print('ccc')
    return {'error': 'Login first !'}, 401

    