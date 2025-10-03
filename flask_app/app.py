from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "votre_clé_secrète_ici"  # Remplacez par une clé sécurisée en production

# URL de base de l'API (à ajuster selon Docker Compose)
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8007")

@app.route('/')
def index():
    if 'pseudo' not in session:
        return redirect(url_for('login'))
    try:
        response = requests.get(f"{API_BASE_URL}/colis/all", headers={"Authorization": f"Bearer {session['access_token']}"})
        colis_list = response.json() if response.status_code == 200 else []
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"Liste des colis récupérée à {current_time} le {datetime.now().strftime('%d/%m/%Y')}")
        return render_template('index.html', colis_list=colis_list, pseudo=session.get('pseudo'))
    except requests.RequestException as e:
        flash(f"Erreur de connexion à l'API : {str(e)}", "error")
        return render_template('index.html', colis_list=[], pseudo=session.get('pseudo'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        mot_de_passe = request.form['mot_de_passe']
        try:
            response = requests.post(f"{API_BASE_URL}/auth/login", json={"pseudo": pseudo, "mot_de_passe": mot_de_passe})
            response_data = response.json()
            if response.status_code == 200:
                session['pseudo'] = response_data['pseudo']
                session['access_token'] = response_data['access_token']
                flash("Connexion réussie !", "success")
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"Connexion réussie pour {pseudo} à {current_time} le {datetime.now().strftime('%d/%m/%Y')}")
                return redirect(url_for('index'))
            else:
                flash(response_data.get('detail', "Erreur lors de la connexion"), "error")
        except requests.RequestException as e:
            flash(f"Erreur de connexion à l'API : {str(e)}", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'pseudo' in session:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"Déconnexion de {session['pseudo']} à {current_time} le {datetime.now().strftime('%d/%m/%Y')}")
    session.pop('pseudo', None)
    session.pop('access_token', None)
    flash("Déconnecté.", "success")
    return redirect(url_for('login'))

@app.route('/colis/view', methods=['GET', 'POST'])
def view_colis():
    if 'pseudo' not in session:
        flash("Veuillez vous connecter.", "error")
        return redirect(url_for('login'))
    colis = None
    if request.method == 'POST':
        colis_id = request.form['colis_id']
        try:
            response = requests.get(f"{API_BASE_URL}/colis/{colis_id}", headers={"Authorization": f"Bearer {session['access_token']}"})
            if response.status_code == 200:
                colis = response.json()
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"Colis {colis_id} récupéré à {current_time} le {datetime.now().strftime('%d/%m/%Y')}")
            else:
                flash(response.json().get('detail', "Colis non trouvé"), "error")
        except requests.RequestException as e:
            flash(f"Erreur : {str(e)}", "error")
    return render_template('view_colis.html', colis=colis)

if __name__ == "__main__":
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"Démarrage de l'interface d'affichage à {current_time} le {datetime.now().strftime('%d/%m/%Y')}")
    app.run(host='0.0.0.0', port=5000, debug=True)