# LearnPath AI 🧠
### AI-Powered Adaptive Personalized Learning Path Recommender
**HCLTech AMPLIFIED Hackathon 2026**

---

## 📋 Project Overview

LearnPath AI is a full-stack AI-powered learning assistant that creates personalized, prerequisite-aware learning roadmaps based on a learner's goals, current skills, and learning preferences.

It demonstrates a complete end-to-end AI pipeline: **User Goal → Learner Profile → Skill Gap → Prerequisite-Aware Path → Hybrid Recommendations → Explanations → Assessment → Adaptive Learning**.

---

## 🎯 Problem Statement

Learning resources are abundant, but learners struggle to:
- Identify exactly which skills they need for their target role
- Find the right sequence to learn skills (respecting prerequisites)
- Get personalized recommendations based on their unique starting point
- Receive adaptive feedback after assessments
- Understand *why* a resource is recommended

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 AI Goal Understanding | LLM extracts structured skill requirements from natural-language goals |
| 📊 Skill Gap Analysis | Quantifies gaps between current and target proficiency per skill |
| 🕸️ Knowledge Graph | NetworkX prerequisite graph ensures correct learning order |
| 🔍 Semantic Search | Sentence Transformers + FAISS for semantic resource retrieval |
| 🏆 Hybrid Ranking | 6-factor weighted scoring (skill gap + goal + prerequisites + difficulty + preference + feedback) |
| 💡 Explainability | Every recommendation includes a human-readable explanation |
| 🔄 Adaptive Engine | Quiz results dynamically update skill proficiency and unlock/block next paths |
| 🤖 AI Assistant | Conversational assistant with learner profile context |
| ⚡ Demo Mode | Full working demonstration without any API key |

---

## 🏗️ Architecture

```
USER
  ↓
STREAMLIT FRONTEND (frontend/app.py)
  ↓
FASTAPI BACKEND (backend/main.py)
  ↓
LEARNER PROFILE (database/models.py + routes/profile.py)
  ↓
GOAL UNDERSTANDING (services/llm_service.py — Gemini/OpenAI + keyword fallback)
  ↓
SKILL GAP ANALYZER (ml/skill_gap.py)
  ↓
KNOWLEDGE GRAPH (ml/knowledge_graph.py — NetworkX)
  ↓
EMBEDDING SEARCH (ml/embeddings.py — SentenceTransformers + FAISS)
  ↓
HYBRID RECOMMENDATION ENGINE (ml/ranking.py — 6 weighted factors)
  ↓
PERSONALIZED LEARNING PATH (ml/recommender.py)
  ↓
LLM EXPLANATIONS + AI ASSISTANT (services/llm_service.py)
  ↓
QUIZ + PROGRESS + FEEDBACK (routes/assessment.py + progress.py)
  ↓
ADAPTIVE LEARNING ENGINE (assessment scoring → skill update → path unlock)
  ↓
UPDATED LEARNING PATH
```

---

## 🤖 AI/ML Approach

### Hybrid Recommendation Score
```
Final Score = 
    30% × Skill Gap Match      (addresses your highest-priority gaps)
  + 25% × Goal Relevance       (aligned with your career target)
  + 20% × Prerequisite Fit     (prerequisites already satisfied)
  + 10% × Difficulty Fit       (matches your experience level)
  + 10% × Learning Preference  (matches project-based / video / etc.)
  +  5% × Feedback Score       (community rating)
```

### Knowledge Graph
- Built from `data/prerequisites.csv` using NetworkX DiGraph
- Topological sort ensures correct phase ordering
- Prerequisite checking blocks locked skills dynamically

### Adaptive Learning
```
Quiz Score ≤ 40%  → Beginner   → Revision resources
Quiz Score 41-70% → Developing → Practice project recommended  
Quiz Score 71-85% → Proficient → Next skill unlocked
Quiz Score 86-100%→ Advanced   → Advanced path unlocked
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Python, Streamlit, Plotly |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Database | SQLite (default), SQLAlchemy ORM |
| ML | Pandas, NumPy, Scikit-learn |
| NLP/Embeddings | Sentence Transformers (all-MiniLM-L6-v2), FAISS |
| Knowledge Graph | NetworkX |
| LLM | Google Gemini / OpenAI (configurable) |
| Visualization | Plotly (radar, bar, gauge, progress charts) |

---

## 📂 Project Structure

```
personalized-learning-ai/
├── frontend/
│   ├── app.py                    # Main Streamlit entry point
│   ├── pages/
│   │   ├── 1_Home.py             # Welcome dashboard + gauge
│   │   ├── 2_Profile.py          # Learner onboarding form  
│   │   ├── 3_Skill_Gap.py        # Gap analysis charts
│   │   ├── 4_Learning_Path.py    # Visual phase roadmap
│   │   ├── 5_Recommendations.py  # Scored recommendation cards
│   │   ├── 6_Assessments.py      # Quiz engine + adaptive feedback
│   │   ├── 7_Progress.py         # Progress charts + milestones
│   │   └── 8_AI_Assistant.py     # Conversational AI chat
│   └── utils/
│       ├── api.py                # Backend API client
│       └── demo_data.py          # Demo mode data (Santhiya)
├── backend/
│   ├── main.py                   # FastAPI app + CORS + lifespan
│   ├── routes/
│   │   ├── profile.py            # POST/GET /api/profile
│   │   ├── analysis.py           # POST /api/analyze-goal, /api/skill-gap
│   │   ├── recommendations.py    # POST /api/recommendations, learning-path
│   │   ├── assessment.py         # GET/POST /api/assessment
│   │   ├── progress.py           # GET/POST /api/progress, /api/feedback
│   │   ├── chat.py               # POST /api/chat
│   │   └── dashboard.py          # GET /api/dashboard/{user_id}
│   ├── services/
│   │   └── llm_service.py        # Gemini/OpenAI + keyword fallback
│   └── schemas/
│       └── schemas.py            # All Pydantic request/response models
├── ml/
│   ├── skill_gap.py              # Gap calculation + readiness score
│   ├── knowledge_graph.py        # NetworkX prerequisite graph
│   ├── embeddings.py             # SentenceTransformers + FAISS
│   ├── ranking.py                # 6-factor hybrid scoring
│   └── recommender.py            # Recommendation orchestrator
├── data/
│   ├── courses.csv               # 105 curated courses
│   ├── projects.csv              # 30 hands-on projects
│   ├── skills.csv                # 30 skills with role targets
│   ├── prerequisites.csv         # Skill prerequisite graph
│   └── quizzes.json              # 8 assessments (40 questions)
├── database/
│   ├── database.py               # SQLAlchemy engine + session
│   ├── models.py                 # 13 ORM models
│   └── seed.py                   # Data seeder + demo user
├── tests/
│   └── test_ml.py                # Smoke tests for ML modules
├── .env.example                  # Environment variable template
├── requirements.txt              # All Python dependencies
├── Dockerfile                    # Docker build
└── README.md
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- pip

### 1. Clone or extract the project
```bash
cd personalized-learning-ai
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
copy .env.example .env
# Edit .env and set your LLM_API_KEY (or leave blank for demo mode)
```

### 5. Seed the database
```bash
python database/seed.py
```

---

## 🚀 Running the Application

### Terminal 1 — Start Backend
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
API docs available at: http://localhost:8000/docs

### Terminal 2 — Start Frontend
```bash
streamlit run frontend/app.py --server.port 8501
```
Open: http://localhost:8501

---

## 🌐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | LLM provider: `gemini` or `openai` |
| `LLM_API_KEY` | *(empty)* | Your API key |
| `LLM_MODEL` | *(auto)* | Model override (e.g. `gemini-1.5-flash`) |
| `DATABASE_URL` | `sqlite:///./learnpath.db` | Database connection string |
| `BACKEND_URL` | `http://localhost:8000` | Backend URL for the frontend |

---

## ⚡ Demo Mode

The application **works without any API key** in demo mode:
- Pre-built learner profile: **Santhiya, AI Engineer**
- Rule-based goal and skill extraction
- Local hybrid recommendation engine
- Demo learning roadmap and quiz results
- Keyword-based AI assistant responses

---

## 📖 API Documentation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/profile` | POST | Create/update learner profile |
| `/api/profile/{user_id}` | GET | Retrieve learner profile |
| `/api/analyze-goal` | POST | Extract goal info from text |
| `/api/skill-gap` | POST | Calculate skill gaps |
| `/api/recommendations` | POST | Get personalized recommendations |
| `/api/learning-path` | POST | Generate learning roadmap |
| `/api/learning-path/{user_id}` | GET | Retrieve saved roadmap |
| `/api/assessment/{skill}` | GET | Get quiz for a skill |
| `/api/assessment/result` | POST | Submit quiz answers |
| `/api/progress` | POST | Update course progress |
| `/api/progress/{user_id}` | GET | Get progress summary |
| `/api/feedback` | POST | Submit resource feedback |
| `/api/chat` | POST | AI assistant conversation |
| `/api/dashboard/{user_id}` | GET | Dashboard summary |

---

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

---

## 🐳 Docker

```bash
docker build -t learnpath-ai .
docker run -p 8000:8000 -p 8501:8501 --env-file .env learnpath-ai
```

---

## 📈 Judging Criteria Alignment

| Criterion (Weight) | How We Address It |
|--------------------|-------------------|
| **Functionality (25%)** | Complete end-to-end flow: profile → skill gap → recommendations → path → assessment → adaptation |
| **AI/ML Implementation (20%)** | SentenceTransformers + FAISS + NetworkX KG + 6-factor hybrid ranking + LLM goal extraction |
| **Problem Understanding (20%)** | Addresses real learning challenges: right sequence, personalization, explainability, adaptation |
| **Innovation (15%)** | Hybrid recommendation engine + prerequisite-aware paths + adaptive unlocking post-assessment |
| **Performance & Code Quality (10%)** | Modular architecture, Pydantic validation, SQLAlchemy ORM, graceful error handling |
| **User Experience (10%)** | Premium dark UI, gauges, radar charts, roadmap visualization, conversational assistant |

---

## 🔮 Future Improvements

1. **Collaborative Filtering** — learn from aggregated learner behavior
2. **Video Integration** — embed actual course videos from YouTube / Coursera
3. **PDF Upload** — let learners paste a job description to auto-set career goal
4. **Multi-language Support** — support Tamil, Hindi, and other regional languages
5. **Mobile App** — React Native companion app
6. **Real-time Progress Sync** — WebSocket-based live progress updates
7. **Certificate Tracking** — connect with LinkedIn Learning / Coursera APIs
8. **Group Learning** — team-based learning path recommendations

---

## 👥 Team

| Role | Name |
|------|------|
| Lead Developer | *Your Name* |
| AI/ML Engineer | *Team Member* |
| Frontend Developer | *Team Member* |
| Data Engineer | *Team Member* |

---

*Built for HCLTech AMPLIFIED Hackathon 2026 — LearnPath AI Team*
