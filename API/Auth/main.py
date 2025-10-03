from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import bcrypt
import jwt
from datetime import datetime, timedelta

app = FastAPI()

# Configuration
SECRET_KEY = "votre_clé_secrète_ici"  # Remplacez par une clé sécurisée en production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Connexion MongoDB (asynchrone avec motor)
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient("mongodb://172.17.32.196:27017/")
    app.database = app.mongodb_client["logistique"]
    app.utilisateurs_collection = app.database["utilisateurs"]
    # Créer un index unique sur pseudo pour éviter les doublons
    await app.utilisateurs_collection.create_index("pseudo", unique=True)

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Modèle pour validation des données reçues
class UserLogin(BaseModel):
    pseudo: str
    mot_de_passe: str

# Modèle pour l'inscription (optionnel, si vous voulez des champs supplémentaires)
class UserSignup(BaseModel):
    pseudo: str
    mot_de_passe: str

# Fonction pour créer un token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Route pour l'authentification
@app.post("/login", description="Authentifie un utilisateur et retourne un token JWT")
async def login(user: UserLogin):
    try:
        # Recherche l'utilisateur dans la base
        utilisateur = await app.utilisateurs_collection.find_one({"pseudo": user.pseudo})
        if utilisateur is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # Vérifie le mot de passe
        if not bcrypt.verify(user.mot_de_passe, utilisateur["mot_de_passe"]):
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")

        # Créer un token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": utilisateur["pseudo"]}, expires_delta=access_token_expires
        )

        return {
            "message": "Connexion réussie",
            "pseudo": utilisateur["pseudo"],
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# Route pour l'inscription
@app.post("/signup", description="Crée un nouvel utilisateur")
async def signup(user: UserSignup):
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = await app.utilisateurs_collection.find_one({"pseudo": user.pseudo})
        if existing_user:
            raise HTTPException(status_code=400, detail=f"L'utilisateur avec le pseudo {user.pseudo} existe déjà")

        # Hacher le mot de passe
        hashed_password = bcrypt.hash(user.mot_de_passe)
        nouveau_user = {
            "pseudo": user.pseudo,
            "mot_de_passe": hashed_password
        }

        # Insérer le nouvel utilisateur
        result = await app.utilisateurs_collection.insert_one(nouveau_user)
        created_user = await app.utilisateurs_collection.find_one({"_id": result.inserted_id})

        if not created_user:
            raise HTTPException(status_code=500, detail="Erreur lors de la création de l'utilisateur")

        return {"message": "Compte créé avec succès", "pseudo": user.pseudo}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")