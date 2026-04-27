from tinydb import TinyDB, Query

db = TinyDB("database.json")
recipes = db.table("recipes")