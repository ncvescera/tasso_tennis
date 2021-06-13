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
    # controlla che l'utente sia autenticato
    if current_user.is_authenticated:
        if current_user.landowner:
            user_id = current_user.id

            dati = Field.query.filter_by(landowner_id=user_id)  # prende tutti i campi
            dati_json = [x.as_dict() for x in dati]             # converte il risultato in dizionario per poter essere inviato a JS

            return json.dumps({'rep': dati_json}), 200          # ritorna i dati

        else:
            dati = Field.query.all()                    # prende tutti i campi
            dati_json = [x.as_dict() for x in dati]     # converte il risultato in dizionario per poter essere inviato a JS

            return json.dumps({'rep': dati_json}), 200

    return json.dumps({'error': 'Login first !'}), 401


@app.route('/api/fields', methods=['POST'])
@login_required
def add_field():
    if current_user.is_authenticated and current_user.landowner:    
        user_id = current_user.id

        # prende i valori passatigli
        name        = request.form['name']
        description = request.form['description']
        address = request.form['address']
        available_from = datetime.strptime(request.form['available_from'], '%H:%M').time()  # da stringa converte in datetime.time
        available_to = datetime.strptime(request.form['available_to'], '%H:%M').time()
        price_h = request.form['price_h']

        # creo il nuovo Field da aggiungere al db
        new_field = Field(
            name=name, 
            description=description, 
            address=address, 
            available_from=available_from, 
            available_to=available_to,
            price_h=price_h,
            landowner_id=user_id
            )

        # prova ad aggiungere il campo
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

        # prova a trovare il campo da eliminare
        to_delete = Field.query.filter_by(id=id, landowner_id=user_id).first()
        if to_delete:                       # se viene trovato lo elimina
            name = to_delete.name
            field_id = to_delete.id
            db.session.delete(to_delete)
            db.session.commit()
            
            # elimina in cascata anche le prenotazioni reltive a quel campo
            prenotazioni_to_delete = Prenotation.query.filter_by(field_id=field_id).all()
            for elem in prenotazioni_to_delete:
                db.session.delete(elem)
                db.session.commit()

            return json.dumps({'message': f'Campo {name} eliminato con successo !'}), 200

        return json.dumps({'error': 'Campo inesistente !'}), 400

    return json.dumps({'error': 'Login first !'}), 401


@app.route('/api/fields', methods=['PUT'])
@login_required
def update_field():
    if current_user.is_authenticated and current_user.landowner:
        name = request.form['name']
        description = request.form['description']
        address = request.form['address']
        field_id = request.form['field_id']

        to_update = Field.query.filter_by(id=field_id).first()
        if to_update:
            to_update.name = name
            to_update.description = description
            to_update.address = address

            try:
                db.session.commit()
            except:
                return json.dumps({'error': 'Nome del campo gia\' esistente !'}), 400
                
            return json.dumps({'message': f'Campo {name} aggiornato con successo !'}), 200
 
        return json.dumps({'error': 'Campo inesistente !'}), 400

    return json.dumps({'error': 'Login first !'}), 401

@app.route('/api/prenotations', methods=['POST'])
@login_required
def add_prenotation():
    def diff_time_time(start, end):
        """
            Funzione effettuare la differenza tra due ore.
            Ritorna la differenza tra le due ore in float.
        """

        diff = end - start
        secs = diff.seconds
        minutes = ((secs/60)%60)/60.0
        hours = secs/3600
     
        return hours

    def validate_prenotation(prenotazione):
        """
            Funzione per la validazione della prenotazione.
             - Controlla che la data non sia antecedente a quella di oggi.
             - Controlla che l'ora della prenotazione rispetti gli orari del campo
             - Controlla che la prenotazione non si sovrapponga con altre prenotazioni
        """

        today = datetime.today().date() # prende la data di oggi

        # controlla che la data di prenotazione non sia passata
        if prenotazione.date >= today:
            prenotazioni_same_date = Prenotation.query.filter_by(date=prenotazione.date)    # prende tutte le prenotazioni fatte in quella data

            s = prenotazione.start  # ora di inizio prenotazione
            e = prenotazione.end    # ora di fine prenotazione

            # controlla che l'ora di inizio e fine non siano invertite
            if s > e:
                return False, 'L\'ora non e\' corretta !'

            # controllo che la prenotazione sia di almeno 1 ora
            ss =  datetime.strptime(str(s), '%H:%M:%S')
            ee =  datetime.strptime(str(e), '%H:%M:%S')

            if diff_time_time(ss, ee) < 1.0:
                return False, 'Prenota almeno 1 ora !'

            # controlla che l'ora di prenotazione rispetti gli orari del campo
            campo = Field.query.filter_by(id=prenotazione.field_id).first() # prende il campo in questione

            if s >= campo.available_from and e <= campo.available_to:
                pass
            else:
                return False, 'La tua prenotazione non rispetta gli orari del campo !'

            # controlla che la prenotazione non si sovrapponga con altre
            for elem in prenotazioni_same_date:
                i = elem.start
                j = elem.end

                if s < i and e <= i:
                    pass
                elif s >= j and e > s:
                    pass
                else:
                    return False, 'Il campo e\' prenotato per quell\'ora !'
            
            # se arriva fino qui vuol dire che la prenotazione e' valida !!
            return True, ''

        else:
            return False, 'Controlla la data !'

    # controlla che l'utente sia un utente normale
    if current_user.is_authenticated and current_user.landowner == False:    
        user_id = current_user.id

        # prende i dati per la nuova prenotazione
        field_id = request.form['field_id']
        start = datetime.strptime(request.form['da'], '%H:%M')
        end   = datetime.strptime(request.form['a'], '%H:%M')
        date =  datetime.strptime(request.form['giorno'], '%Y-%m-%d').date()
        
        price_h = Field.query.filter_by(id=field_id).first().price_h
        price = price_h * diff_time_time(start, end)    # calcola il prezzo totale
        
        # crea la nuova prenotazione
        new_prenotation = Prenotation(
            field_id=field_id, 
            player_id=user_id, 
            date=date,
            start=start.time(),
            end=end.time(),
            price=price)

        # controlla se la prenotazione e' valida
        is_valid = validate_prenotation(new_prenotation)

        if is_valid[0] == False:
            return json.dumps({'error': f'Impossibile effettuare la prenotazione: {is_valid[1]}' }), 400

        # prova ad aggiungere la prenotazione al db
        try:
            db.session.add(new_prenotation)
            db.session.commit()
        except:
            return json.dumps({'error': 'Impossibile effettuare la prenotazione!'}), 400

        # se arriva fino qui vuol dire che la prenotazione e' stata aggiunta al db
        return json.dumps({'message': 'Prenotazione effettuata con successo !'}), 200        

    return json.dumps({'error': 'Login first !'}), 401


@app.route('/api/prenotations', methods=['GET'])
@login_required
def get_all_prenotations():
    # controlla che l'utente sia autenticato
    if current_user.is_authenticated:
        # distingue le due tipologie di utenti
        if current_user.landowner == False:
            user_id = current_user.id
            
            # effettua la join tra Prenotazione e Campo per ottenere il nome del campo
            prenotazioni = db.session.query(
                Prenotation.date, 
                Prenotation.start, 
                Prenotation.end, 
                Prenotation.price, 
                Field.name,
                Prenotation.id
                    ).join(
                        Field, 
                        Prenotation.field_id == Field.id
                            ).filter(Prenotation.player_id == user_id)
            
            # converte le prenotazioni in JSON per essere ritornate
            dati_json = []
            for elem in prenotazioni:
                tmp = {
                    'date': str(elem[0]),
                    'start': str(elem[1])[:-3],
                    'end': str(elem[2])[:-3],
                    'price': str(round(elem[3], 1)),
                    'name': str(elem[4]),
                    'id': str(elem[5])
                }
        
                dati_json.append(tmp)
            
            return json.dumps({'rep': dati_json}), 200

        else:
            user_id = current_user.id

            # effettua la join tra Prenotazione e Campo per ottenere il nome del campo
            prenotazioni = db.session.query(
                Prenotation.date, 
                Prenotation.start, 
                Prenotation.end, 
                Prenotation.price, 
                Field.name,
                Prenotation.id,
                User.username
                    ).join(
                        Field,
                        Prenotation.field_id == Field.id
                            ).join(
                                User, 
                                Prenotation.player_id == User.id
                                ).filter(Field.landowner_id == user_id)
            
            # converte le prenotazioni in JSON per essere ritornate
            dati_json = []
            for elem in prenotazioni:
                tmp = {
                    'date': str(elem[0]),
                    'start': str(elem[1])[:-3],
                    'end': str(elem[2])[:-3],
                    'price': str(round(elem[3], 1)),
                    'name': str(elem[4]),
                    'id': str(elem[5]),
                    'username': str(elem[6])
                }
        
                dati_json.append(tmp)
            
            return json.dumps({'rep': dati_json}), 200

    return json.dumps({'error': 'Login first !'}), 401


@app.route('/api/prenotations/<int:id>', methods=['DELETE'])
@login_required
def delete_prenotation(id):
    # controlla che l'utente sia un utente normale
    if current_user.is_authenticated and current_user.landowner == False:
        user_id = current_user.id

        # elimina la prenotazione
        to_delete = Prenotation.query.filter_by(id=id, player_id=user_id).first()
        if to_delete:
            db.session.delete(to_delete)
            db.session.commit()

            return json.dumps({'message': f'Prenotazione eliminata con successo !'}), 200
        
        return json.dumps({'error': 'Prenotazione inesistente !'}), 400

    return json.dumps({'error': 'Login first !'}), 401