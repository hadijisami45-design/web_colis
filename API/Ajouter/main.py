from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from datetime import datetime
import os
from typing import Optional
from pydantic import BaseModel

app = FastAPI()


MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://172.17.32.196:27017/')
try:
    client = MongoClient(MONGO_URI)
    client.server_info()
    db = client['colis_db']
    colis_collection = db['colis']
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

class ColisCreate(BaseModel):
    destinataire: str
    adresse: str
    poids: float
    statut: Optional[str] = "En attente"
    created_by: str

class ColisResponse(BaseModel):
    message: str
    colis_id: str

@app.post("/colis", response_model=ColisResponse, status_code=201)
async def ajouter_colis(colis: ColisCreate):
    try:
        nouveau_colis = {
            'destinataire': colis.destinataire,
            'adresse': colis.adresse,
            'poids': colis.poids,
            'statut': colis.statut,
            'created_by': colis.created_by,
            'date_creation': datetime.utcnow(),
            'date_mise_a_jour': datetime.utcnow()
        }
        result = colis_collection.insert_one(nouveau_colis)
        return ColisResponse(message='Colis ajouté avec succès', colis_id=str(result.inserted_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)