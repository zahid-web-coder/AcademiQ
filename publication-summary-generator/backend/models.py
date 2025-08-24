# models.py
from datetime import datetime
from bson.objectid import ObjectId
from typing import List, Dict, Any

# ---------- Collections ----------
def get_faculty_model(db):
    return db["faculty"]

def get_publication_model(db):
    return db["publications"]

# ---------- Indexes ----------
def ensure_indexes(db):
    # Safe to call many times
    get_faculty_model(db).create_index([("_id", 1)], unique=True)
    get_publication_model(db).create_index([("faculty_id", 1)])
    get_publication_model(db).create_index([("created_at", -1)])

# ---------- Faculty ----------
def create_faculty(db, faculty_id: str, name: str, department: str) -> Dict[str, Any]:
    doc = {
        "_id": faculty_id,              # human-readable id
        "name": name,
        "department": department,
        "created_at": datetime.utcnow(),
    }
    get_faculty_model(db).update_one({"_id": faculty_id}, {"$setOnInsert": doc}, upsert=True)
    # return the stored doc
    return get_faculty_model(db).find_one({"_id": faculty_id})

def get_faculty(db, faculty_id: str):
    return get_faculty_model(db).find_one({"_id": faculty_id})

def list_faculty(db):
    return list(get_faculty_model(db).find({}))

# ---------- Publications ----------
def create_publication(db, faculty_id: str, title: str, abstract: str, summary: str | None = None):
    doc = {
        "faculty_id": faculty_id,
        "title": title,
        "abstract": abstract,
        "summary": summary or "",
        "created_at": datetime.utcnow(),
    }
    result = get_publication_model(db).insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc

def create_publications_batch(db, faculty_id: str, items: List[Dict[str, str]]):
    """items: [{title, abstract}, ...]"""
    now = datetime.utcnow()
    docs = [{
        "faculty_id": faculty_id,
        "title": it.get("title", "Untitled"),
        "abstract": it.get("abstract", ""),
        "summary": "",
        "created_at": now,
    } for it in items]

    if not docs:
        return []

    result = get_publication_model(db).insert_many(docs)
    # attach ids
    for i, _id in enumerate(result.inserted_ids):
        docs[i]["*_id"] = _id  # temporary marker; we’ll convert in app serializer
        docs[i]["_id"] = _id
    return docs

def get_publication(db, pub_id: str):
    return get_publication_model(db).find_one({"_id": ObjectId(pub_id)})

def list_publications(db, faculty_id: str | None = None):
    q = {"faculty_id": faculty_id} if faculty_id else {}
    return list(get_publication_model(db).find(q).sort("created_at", -1))

def save_summary(db, publication_id: str, summary_text: str, mode: str = "extractive"):
    get_publication_model(db).update_one(
        {"_id": ObjectId(publication_id)},
        {"$set": {f"{mode}_summary": summary_text, "updated_at": datetime.utcnow()}}
    )
    return True
