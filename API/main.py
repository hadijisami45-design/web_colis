from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from auth.auth import router as auth_router
from ajouter.ajouter import router as ajouter_router

app = FastAPI()

# Connexion MongoDB
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient("mongodb://172.17.32.196:27017/")
    app.database = app.mongodb_client["logistique"]
    app.utilisateurs_collection = app.database["utilisateurs"]
    app.colis_collection = app.database["colis"]
    await app.utilisateurs_collection.create_index("pseudo", unique=True)

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Inclure les routeurs
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ajouter_router, prefix="/colis", tags=["colis"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)