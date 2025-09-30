from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# Connexion MongoDB
client = MongoClient("mongodb://172.17.32.196:27017/")
db = client["logistique"]
colis_collection = db["colis"]

# Convertir un document Mongo en JSON
def colis_serializer(colis) -> dict:
    return {
        "id": str(colis["_id"]),
        "numero_suivi": colis["numero_suivi"],
        "destinataire": colis["destinataire"],
        "adresse": colis["adresse"],
        "statut": colis["statut"]
    }

# Route pour afficher un colis par ID
@app.get("/colis/{colis_id}")
def get_colis(colis_id: str):
    colis = colis_collection.find_one({"_id": ObjectId(colis_id)})
    if not colis:
        raise HTTPException(status_code=404, detail="Colis introuvable")
    return colis_serializer(colis)
