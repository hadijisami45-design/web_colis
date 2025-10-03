from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel

app = FastAPI()

# Initialisation de la connexion MongoDB lors du démarrage
@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb://172.17.32.196:27017/")
    app.database = app.mongodb_client["logistique"]
    app.colis_collection = app.database["colis"]
    # Créer un index unique sur numero_suivi pour éviter les doublons
    app.colis_collection.create_index("numero_suivi", unique=True)

# Fermeture de la connexion MongoDB lors de l'arrêt
@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

# Modèle pour validation des données reçues
class Colis(BaseModel):
    numero_suivi: str
    destinataire: str
    adresse: str
    statut: str

# Convertir un document Mongo en JSON
def colis_serializer(colis) -> dict:
    if not all(key in colis for key in ["numero_suivi", "destinataire", "adresse", "statut"]):
        raise HTTPException(status_code=500, detail="Document colis incomplet")
    return {
        "id": str(colis["_id"]),
        "numero_suivi": colis["numero_suivi"],
        "destinataire": colis["destinataire"],
        "adresse": colis["adresse"],
        "statut": colis["statut"]
    }

# Route pour ajouter un colis
@app.post("/colis", description="Ajoute un nouveau colis à la base de données")
async def add_colis(colis: Colis):
    try:
        # Vérifier si un colis avec le même numero_suivi existe déjà
        existing_colis = app.colis_collection.find_one({"numero_suivi": colis.numero_suivi})
        if existing_colis:
            raise HTTPException(status_code=400, detail=f"Le colis avec le numéro de suivi {colis.numero_suivi} existe déjà")

        # Insérer le nouveau colis
        new_colis = dict(colis)
        result = app.colis_collection.insert_one(new_colis)

        # Récupérer le colis créé
        created_colis = app.colis_collection.find_one({"_id": result.inserted_id})
        if not created_colis:
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération du colis créé")

        return colis_serializer(created_colis)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")