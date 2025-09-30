import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://172.17.32.196:27017")
db = client["ma_base"]
