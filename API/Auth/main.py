from fastapi import FastAPI, HTTPException
from auth import db
from pydantic import BaseModel
from passlib.hash import bcrypt


app = FastAPI()


# Modèle de données pour l’utilisateur
class UserLogin(BaseModel):
    pseudo: str
    mot_de_passe: str

@app.post("/login")
async def login(user: UserLogin):
    # Recherche l'utilisateur dans la base
    utilisateur = await db["utilisateurs"].find_one({"pseudo": user.pseudo})

    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Vérifie le mot de passe
    if not bcrypt.verify(user.mot_de_passe, utilisateur["mot_de_passe"]):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    return {"message": "Connexion réussie", "pseudo": utilisateur["pseudo"]}

    hashed_password = bcrypt.hash(user.mot_de_passe)
    nouveau_user = {
        "pseudo": user.pseudo,
        "mot_de_passe": hashed_password
    }
    await db["utilisateurs"].insert_one(nouveau_user)

    return {"message": "Compte créé avec succès", "pseudo": user.pseudo}