from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from bson import ObjectId
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'votre_cle_secrete_tres_longue_et_complexe')


MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://172.17.32.196:27017/')
client = MongoClient(MONGO_URI)
db = client['colis_db']
colis_collection = db['colis']
users_collection = db['users']


API_AFFICHAGE_URL = os.environ.get('API_AFFICHAGE_URL', 'http://localhost:8000')
API_AJOUTER_URL = os.environ.get('API_AJOUTER_URL', 'http://localhost:8001')
API_AUTH_URL = os.environ.get('API_AUTH_URL', 'http://localhost:8002')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        response = requests.get(f"{API_AFFICHAGE_URL}/colis")
        colis = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Erreur: {e}")
        colis = []
    return render_template('index.html', colis=colis, username=session.get('username'))

@app.route('/mes_colis')
def mes_colis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        user_id = session['user_id']
        response = requests.get(f"{API_AFFICHAGE_URL}/colis")
        all_colis = response.json() if response.status_code == 200 else []
        mes_colis = [colis for colis in all_colis if colis.get('created_by') == user_id]
    except Exception as e:
        print(f"Erreur: {e}")
        mes_colis = []
    return render_template('mes_colis.html', colis=mes_colis, username=session.get('username'))
@app.route('/recherche_colis')
def recherche_colis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('q', '')
    colis_trouves = []
    
    if query:
        try:
            response = requests.get(f"{API_AFFICHAGE_URL}/colis")
            all_colis = response.json() if response.status_code == 200 else []
            
            
            for colis in all_colis:
                if (query.lower() in colis.get('destinataire', '').lower() or 
                    query.lower() in colis.get('adresse', '').lower() or 
                    query.lower() in colis.get('statut', '').lower() or
                    query.lower() in str(colis.get('_id', '')).lower()):
                    colis_trouves.append(colis)
                    
        except Exception as e:
            print(f"Erreur: {e}")
    
    return render_template('recherche_colis.html', 
                         colis=colis_trouves, 
                         query=query, 
                         username=session.get('username'))

@app.route('/ajouter_colis')
def page_ajouter_colis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('ajouter_colis.html', username=session.get('username'))

@app.route('/ajouter_colis', methods=['POST'])
def ajouter_colis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    colis_data = {
        'destinataire': request.form['destinataire'],
        'adresse': request.form['adresse'],
        'poids': float(request.form['poids']),
        'statut': 'En attente',
        'created_by': session['user_id']
    }
    
    try:
        response = requests.post(f"{API_AJOUTER_URL}/colis", json=colis_data)
        if response.status_code == 201:
            return redirect(url_for('mes_colis'))
        else:
            return render_template('ajouter_colis.html', 
                                 error="Erreur lors de l'ajout du colis", 
                                 username=session.get('username'))
    except Exception as e:
        return render_template('ajouter_colis.html', 
                             error="Service d'ajout indisponible", 
                             username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            
            response = requests.post(f"{API_AUTH_URL}/login", 
                                   json={'username': username, 'password': password})
            
            if response.status_code == 200:
                user_data = response.json()
                session['user_id'] = user_data['user_id']
                session['username'] = user_data['username']
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Identifiants incorrects')
        except Exception as e:
            print(f"Erreur auth: {e}")
            return render_template('login.html', error='Service d\'authentification indisponible')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        try:
            response = requests.post(f"{API_AUTH_URL}/register", 
                                   json={'username': username, 'password': password, 'email': email})
            
            if response.status_code == 201:
                return render_template('login.html', success='Compte créé avec succès! Vous pouvez maintenant vous connecter.')
            else:
                error = response.json().get('error', 'Erreur lors de l\'inscription')
                return render_template('login.html', error=error)
        except Exception as e:
            print(f"Erreur register: {e}")
            return render_template('login.html', error='Service d\'authentification indisponible')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/colis')
def api_colis():
    try:
        response = requests.get(f"{API_AFFICHAGE_URL}/colis")
        return jsonify(response.json()), response.status_code
    except:
        return jsonify([]), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)