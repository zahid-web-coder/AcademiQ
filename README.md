# 🎓 AcademiQ — Publication Summarizer Backend

AI-powered backend for summarizing research publications.  
Built with **Flask + MongoDB + Hugging Face Transformers**.

---

## 🚀 Features What is done here
- Faculty management (add/list/get)
- Publication management (single + batch add, list, fetch)
- Automatic summarization:
  - Extractive (TextRank)
  - Abstractive (T5)
  - Hybrid (Extractive → Abstractive refinement)
- MongoDB integration for persistence
- REST APIs (tested via Postman collection)

  
---

## ⚙️ Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/zahid-web-coder/AcademiQ.git
   cd AcademiQ/backend
Create a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Copy .env.example → .env and fill values:

env
Copy
Edit
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/
▶️ Run the Server
bash
Copy
Edit
python app.py
App will run at:
👉 http://127.0.0.1:5000

📡 API Endpoints
Health
GET /health

Faculty
POST /add-faculty

GET /faculty

GET /faculty/<faculty_id>

Publications
POST /add-publication

GET /publications?faculty_id=F001

GET /publications/<pub_id>

POST /publications/<pub_id>/summarize/extractive

POST /add-publications-batch

Test Routes
GET /test-extractive

GET /test-abstractive

GET /test-hybrid

🧪 Postman Collection
Import docs/postman_collection.json into Postman to test all endpoints quickly.

🌐 Deployment (Optional)
Recommended: Render / Railway
Update .env with production MONGO_URI.
