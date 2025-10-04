from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from pydantic import BaseModel, EmailStr
from werkzeug.security import generate_password_hash, check_password_hash
import os
from typing import Optional
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError

app = FastAPI(title="API Authentification", version="1.0.0")


MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://172.17.32.196:27017/')
try:
    client = MongoClient(MONGO_URI)
    client.server_info()
    db = client['colis_db']
    users_collection = db['users']
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Modèles Pydantic
class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    message: str
    user_id: str
    username: Optional[str] = None

class LoginResponse(BaseModel):
    message: str
    user_id: str
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):

    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = users_collection.find_one({'username': user.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom d'utilisateur déjà utilisé"
            )
        
        
        existing_email = users_collection.find_one({'email': user.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
        
        
        hashed_password = generate_password_hash(user.password)
        
        nouvel_utilisateur = {
            'username': user.username,
            'password': hashed_password,
            'email': user.email
        }
        
        result = users_collection.insert_one(nouvel_utilisateur)
        
        return UserResponse(
            message="Utilisateur créé avec succès",
            user_id=str(result.inserted_id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du compte: {str(e)}"
        )

@app.post("/login", response_model=LoginResponse)
async def login(user: UserLogin):
    """ 
    Connexion utilisateur 
    """
    try:
        utilisateur = users_collection.find_one({'username': user.username})
        
        if utilisateur and check_password_hash(utilisateur['password'], user.password):
            return LoginResponse(
                message="Connexion réussie",
                user_id=str(utilisateur['_id']),
                username=utilisateur['username']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la connexion: {str(e)}"
        )


@app.get("/users/{username}")
async def get_user_info(username: str):

    try:
        utilisateur = users_collection.find_one({'username': username})
        
        if not utilisateur:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return {
            'user_id': str(utilisateur['_id']),
            'username': utilisateur['username'],
            'email': utilisateur['email']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des informations: {str(e)}"
        )

SECRET_KEY = os.environ.get('SECRET_KEY', 'votre_cle_secrete_ici')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/login-jwt", response_model=Token)
async def login_jwt(user: UserLogin):

    try:
        utilisateur = users_collection.find_one({'username': user.username})
        
        if utilisateur and check_password_hash(utilisateur['password'], user.password):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            expire = datetime.utcnow() + access_token_expires
            
            token_data = {
                "sub": utilisateur['username'],
                "user_id": str(utilisateur['_id']),
                "exp": expire
            }
            
            access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            
            return Token(
                access_token=access_token,
                token_type="bearer"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la connexion: {str(e)}"
        )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8002, reload=True)