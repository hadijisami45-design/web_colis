import motor.motor_asyncio
import asyncio

# Connexion async à MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://172.17.32.196:27017")
db = client["ma_base"]

async def test():
    user = {"nom": "Sami", "email": "sami@example.com"}
    await db["utilisateurs"].insert_one(user)
    result = await db["utilisateurs"].find_one({"nom": "Sami"})
    print(result)
    

if __name__ == "__main__":
    asyncio.run(test())