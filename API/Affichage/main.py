from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import os
from typing import List, Dict, Any

app = FastAPI()


MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://172.17.32.196:27017/')
try:
    client = MongoClient(MONGO_URI)
    client.server_info()  
    db = client['colis_db']
    colis_collection = db['colis']
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/colis", response_model=List[Dict[str, Any]])
async def get_colis():
    try:
        colis = list(colis_collection.find({}))
        for colis_item in colis:
            colis_item['_id'] = str(colis_item['_id'])
        return colis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/colis/{colis_id}")
async def get_colis_by_id(colis_id: str):
    try:
        if not ObjectId.is_valid(colis_id):
            raise HTTPException(status_code=400, detail="Invalid ID format")
        colis = colis_collection.find_one({'_id': ObjectId(colis_id)})
        if colis:
            colis['_id'] = str(colis['_id'])
            return colis
        raise HTTPException(status_code=404, detail="Parcel not found")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)