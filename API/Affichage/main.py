from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

app = FastAPI()

# Initialisation de la connexion MongoDB lors du démarrage
@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb://172.17.32.196:27017/")
    app.database = app.mongodb_client["logistique"]
    app.colis_collection = app.database["colis"]

# Fermeture de la connexion MongoDB lors de l'arrêt
@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

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

# Route pour afficher un colis par ID
@app.get("/colis/{colis_id}", description="Récupère un colis par son ID")
async def get_colis(colis_id: str):
    try:
        # Valider que colis_id est un ObjectId valide
        oid = ObjectId(colis_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de colis invalide")

    try:
        colis = app.colis_collection.find_one({"_id": oid})
        if not colis:
            raise HTTPException(status_code=404, detail="Colis introuvable")
        return colis_serializer(colis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")