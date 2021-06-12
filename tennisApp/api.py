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

        else:
            dati = Field.query.all()
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


@app.route('/api/prenotations', methods=['POST'])
@login_required
def add_prenotation():
    def diff_time_time(start, end):
        diff = end - start
        secs = diff.seconds
        minutes = ((secs/60)%60)/60.0
        hours = secs/3600
        tot = hours + minutes

        return tot

    if current_user.is_authenticated and current_user.landowner == False:    
        user_id = current_user.id

        field_id = request.form['field_id']
        start = datetime.strptime(request.form['da'], '%H:%M')
        end   = datetime.strptime(request.form['a'], '%H:%M')
        date =  datetime.strptime(request.form['giorno'], '%Y-%m-%d').date()
        
        price_h = Field.query.filter_by(id=field_id).first().price_h
        price = price_h * diff_time_time(start, end)
        
        new_prenotation = Prenotation(
            field_id=field_id, 
            player_id=user_id, 
            date=date,
            start=start.time(),
            end=end.time(),
            price=price)

        try:
            db.session.add(new_prenotation)
            db.session.commit()
        except:
            return json.dumps({'error': 'Impossibile effettuare la prenotazione!'}), 400

        return json.dumps({'message': 'Prenotazione effettuata con successo !'}), 200        

    return json.dumps({'error': 'Login first !'}), 401


@app.route('/api/prenotations', methods=['GET'])
@login_required
def get_all_prenotations():
    if current_user.is_authenticated and current_user.landowner == False:
        user_id = current_user.id
        
        prenotazioni = db.session.query(
            Prenotation.date, 
            Prenotation.start, 
            Prenotation.end, 
            Prenotation.price, 
            Field.name
                ).join(
                    Field, 
                    Prenotation.field_id == Field.id
                        ).filter(Prenotation.player_id == user_id)
        
        dati_json = []
        for elem in prenotazioni:
            print(elem)
            tmp = {
                'date': str(elem[0]),
                'start': str(elem[1]),
                'end': str(elem[2]),
                'price': str(round(elem[3], 1)),
                'name': str(elem[4])
            }
    
            dati_json.append(tmp)
        
        return json.dumps({'rep': dati_json}), 200

    return json.dumps({'error': 'Login first !'}), 401
