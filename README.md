# 🎓 AcademiQ — Publication Summarizer Backend

AI-powered backend for summarizing faculty research publications.  
Built with **Flask + MongoDB + Hugging Face Transformers**.

---

## ✅ What’s Already Implemented

### Faculty Management
- Add new faculty  
- List all faculty  
- Get details of one faculty  

### Publication Management
- Add single publication (with automatic summarization)  
- Add multiple publications (batch)  
- List publications (by `faculty_id`)  
- Get one publication (by `id`)  

### Summarization Engine
- Extractive (TextRank)  
- Abstractive (T5)  
- Hybrid (Extractive → Abstractive refinement)  

### Persistence
- MongoDB Atlas integration  

### Testing
- Ready-to-use **Postman collection** with all APIs  

---

## ⚙️ Setup Instructions (Step by Step)

### 1. Clone the repo
```bash
git clone https://github.com/zahid-web-coder/AcademiQ.git
cd AcademiQ/backend
```

2. Create virtual environment

```python -m venv venv
# For Linux/Mac
source venv/bin/activate
# For Windows
venv\Scripts\activate
```
3. Install dependencies

```~pip install -r requirements.txt```

4. Configure Environment Variables

Copy .env.example → .env and fill values:

MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/

5. Run the server

```python app.py```

App will run at:
👉 http://127.0.0.1:5000


---

📡 API Endpoints

🔍 Health

GET /health


👨‍🏫 Faculty

POST /add-faculty → add new faculty

GET /faculty → list all faculty

GET /faculty/<faculty_id> → get single faculty


📄 Publications

POST /add-publication → add one publication

GET /publications?faculty_id=F001 → list by faculty

GET /publications/<pub_id> → fetch one publication

POST /publications/<pub_id>/summarize/extractive → re-summarize one

POST /add-publications-batch → add multiple at once


🧪 Test Routes

GET /test-extractive

GET /test-abstractive

GET /test-hybrid



---

🧪 Postman Collection

Import:

docs/Publication_Summary_Generator.postman_collection.json

All APIs are pre-configured with sample requests.

Change faculty_id and abstract as needed.



---

🌐 Deployment (Optional)

Recommended: Render / Railway

Steps:

1. Push to GitHub


2. Deploy backend


3. Update .env with production MONGO_URI




---

📌 Notes for Team Members

Tousif (Frontend)

Backend base URL → http://127.0.0.1:5000 (local) or deployed Render link.

Call /add-faculty and /add-publication APIs from the frontend.

Display results from /publications?faculty_id=F001.


Hari (Data)

Feed publication data into /add-publication or /add-publications-batch.

Ensure faculty_id, title, and abstract are always provided.

