from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel

app = FastAPI()

# Connexion MongoDB
client = MongoClient("mongodb://172.17.32.196:27017/")
db = client["logistique"]
colis_collection = db["colis"]

# Modèle pour validation des données reçues
class Colis(BaseModel):
    numero_suivi: str
    destinataire: str
    adresse: str
    statut: str

# Convertir un document Mongo en JSON
def colis_serializer(colis) -> dict:
    return {
        "id": str(colis["_id"]),
        "numero_suivi": colis["numero_suivi"],
        "destinataire": colis["destinataire"],
        "adresse": colis["adresse"],
        "statut": colis["statut"]
    }





@app.post("/colis")
def add_colis(colis: Colis):
    new_colis = dict(colis)
    result = colis_collection.insert_one(new_colis)
    created_colis = colis_collection.find_one({"_id": result.inserted_id})
    return colis_serializer(created_colis)

