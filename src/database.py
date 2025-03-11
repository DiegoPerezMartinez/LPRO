"""Módulo para interactuar con la base de datos MongoDB."""
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["lossnt_db"]
collection = db["objects"]

def save_object(name, range_val, is_active):
    """Guardar un objeto en la base de datos"""
    existing_object = collection.find_one({"name": name, "range": range_val})
    if existing_object:
        # Actualizar el estado en lugar de duplicar
        collection.update_one(
            {"_id": existing_object["_id"]},
            {"$set": {"is_active": is_active}}
        )
    else:
        # Insertar nuevo objeto si no existe
        collection.insert_one({
            "name": name,
            "range": range_val,
            "is_active": is_active
        })

def load_objects():
    """Carga los objetos desde la base de datos"""
    return list(collection.find())

def update_object_status(name, range_val, is_active):
    """Actualizar el estado de un objeto en la base de datos"""
    collection.update_one(
        {"name": name, "range": range_val},
        {"$set": {"is_active": is_active}}
    )

def delete_object(name, range_val):
    """Eliminar un objeto de la base"""
    collection.delete_one({"name": name, "range": range_val})
