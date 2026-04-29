from tinydb import TinyDB, Query

db = TinyDB("data/database.json")
recipes = db.table("recipes")