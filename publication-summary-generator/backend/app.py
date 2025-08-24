# app.py
import sys
import traceback
from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from datetime import datetime


from services.summarizer_extractive import extractive_summary
from services.summarizer_abstractive import abstractive_summary
from services.summarizer_hybrid import hybrid_summary

from models import (
    ensure_indexes,
    create_faculty, get_faculty, list_faculty,
    create_publication, create_publications_batch, get_publication, list_publications, save_summary
)

print("🚀 Flask backend starting...", file=sys.stderr)
load_dotenv()

app = Flask(__name__)
CORS(app)

# ---------- Mongo ----------
MONGO_URI = os.getenv("MONGO_URI")
db = None
try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI)
        db = client["publication_summary"]
        ensure_indexes(db)
        print("✅ MongoDB connected", file=sys.stderr)
    else:
        print("⚠️ MongoDB not configured", file=sys.stderr)
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}", file=sys.stderr)

# ---------- Helpers ----------
def _clean(obj):
    """Make Mongo docs JSON-friendly."""
    if obj is None:
        return None
    if isinstance(obj, list):
        return [_clean(x) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, ObjectId):
                out[k] = str(v)
            elif isinstance(v, datetime):
                out[k] = v.isoformat() + "Z"
            else:
                out[k] = _clean(v)
        return out
    return obj

# ---------- Health ----------
@app.get("/health")
def health_check():
    return {"status": "Backend is running!"}

# ---------- Faculty ----------
@app.post("/add-faculty")
def add_faculty():
    if not db:
        return {"error": "Database not connected"}, 500
    data = request.get_json(force=True) or {}
    fid = data.get("faculty_id")
    name = data.get("name")
    dept = data.get("department")
    if not (fid and name and dept):
        return {"error": "faculty_id, name, department are required"}, 400
    doc = create_faculty(db, fid, name, dept)
    return {"message": "✅ Faculty upserted", "faculty": _clean(doc)}, 201

@app.get("/faculty")
def route_list_faculty():
    if not db:
        return {"error": "Database not connected"}, 500
    docs = list_faculty(db)
    return {"faculty": _clean(docs)}

@app.get("/faculty/<fid>")
def route_get_faculty(fid):
    if not db:
        return {"error": "Database not connected"}, 500
    doc = get_faculty(db, fid)
    if not doc:
        return {"error": "Faculty not found"}, 404
    return {"faculty": _clean(doc)}

# ---------- Publications (single) ----------
@app.post("/add-publication")
def add_publication():
    if not db:
        return {"error": "Database not connected"}, 500
    data = request.get_json(force=True) or {}
    faculty_id = data.get("faculty_id")
    title = data.get("title")
    abstract = data.get("abstract")
    if not (faculty_id and title and abstract):
        return {"error": "faculty_id, title, abstract are required"}, 400

    # create
    pub = create_publication(db, faculty_id, title, abstract)

    # extractive summary immediately
    try:
        summary = extractive_summary(abstract)
        save_summary(db, str(pub["_id"]), summary, mode="extractive")
        pub["extractive_summary"] = summary
    except Exception as e:
        traceback.print_exc()
        pub["extractive_summary"] = f"ERROR: {e}"

    return {"message": "✅ Created & summarized", "publication": _clean(pub)}, 201

@app.get("/publications")
def route_list_publications():
    if not db:
        return {"error": "Database not connected"}, 500
    faculty_id = request.args.get("faculty_id")
    docs = list_publications(db, faculty_id=faculty_id)
    return {"publications": _clean(docs)}

@app.get("/publications/<pub_id>")
def route_get_publication(pub_id):
    if not db:
        return {"error": "Database not connected"}, 500
    try:
        doc = get_publication(db, pub_id)
    except Exception:
        return {"error": "Invalid publication id"}, 400
    if not doc:
        return {"error": "Publication not found"}, 404
    return {"publication": _clean(doc)}

@app.post("/publications/<pub_id>/summarize/extractive")
def route_resummarize_extractive(pub_id):
    if not db:
        return {"error": "Database not connected"}, 500
    try:
        doc = get_publication(db, pub_id)
    except Exception:
        return {"error": "Invalid publication id"}, 400
    if not doc:
        return {"error": "Publication not found"}, 404

    try:
        s = extractive_summary(doc.get("abstract", ""))
        save_summary(db, pub_id, s, mode="extractive")
        doc["extractive_summary"] = s
        return {"message": "✅ Re-summarized", "publication": _clean(doc)}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

# ---------- Publications (batch) ----------
@app.post("/add-publications-batch")
def add_publications_batch():
    """
    Body:
    {
      "faculty_id": "F001",
      "publications": [
        {"title": "...", "abstract": "..."},
        {"title": "...", "abstract": "..."}
      ]
    }
    """
    if not db:
        return {"error": "Database not connected"}, 500
    data = request.get_json(force=True) or {}
    fid = data.get("faculty_id")
    items = data.get("publications", [])
    if not fid or not isinstance(items, list) or not items:
        return {"error": "faculty_id and non-empty publications[] required"}, 400

    # insert many
    docs = create_publications_batch(db, fid, items)

    # summarize each
    summarized = []
    for d in docs:
        try:
            s = extractive_summary(d.get("abstract", ""))
            save_summary(db, str(d["_id"]), s, mode="extractive")
            d["extractive_summary"] = s
        except Exception as e:
            d["extractive_summary"] = f"ERROR: {e}"
        summarized.append(d)

    return {"message": f"✅ Created {len(summarized)} publications", "publications": _clean(summarized)}, 201

# ---------- Simple tests ----------
@app.get("/test-extractive")
def test_extractive_route():
    sample_text = (
        "Artificial intelligence (AI) is intelligence demonstrated by machines, "
        "in contrast to the natural intelligence displayed by humans and animals. "
        'Leading AI textbooks define the field as the study of "intelligent agents"...'
    )
    try:
        return {"summary": extractive_summary(sample_text)}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

@app.get("/test-abstractive")
def test_abstractive_route():
    sample_text = (
        "Artificial intelligence (AI) is intelligence demonstrated by machines, "
        "in contrast to the natural intelligence displayed by humans and animals..."
    )
    try:
        return {"summary": abstractive_summary(sample_text)}
    except Exception as e:
        # fall back so it never dies
        return {"warning": f"Abstractive failed: {e}", "summary": extractive_summary(sample_text)}

@app.get("/test-hybrid")
def test_hybrid_route():
    sample_text = (
        "Artificial intelligence (AI) is intelligence demonstrated by machines, "
        "in contrast to the natural intelligence displayed by humans and animals..."
    )
    try:
        return {"summary": hybrid_summary(sample_text)}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

# ---------- Run ----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
