# Production-Ready Webhook Receiver

> Robust webhook receiver with real-time event tracking and monitoring — built for API integration reliability.

![Demo Screenshot](frontend/public/image.png)

## 🌐 Live Links

- **Frontend:** [techstax-assignment-webhook-repo-nt.vercel.app](https://techstax-assignment-webhook-repo-nt.vercel.app/)
- **Backend API:** [echstax-assignment-webhook-repo-iamvamsi1725-vdm3vfi8.apn.leapcell.dev](https://echstax-assignment-webhook-repo-iamvamsi1725-vdm3vfi8.apn.leapcell.dev)
- **Health Check:**[/health endpoint]https://echstax-assignment-webhook-repo-iamvamsi1725-vdm3vfl8.apn.leapcell.dev/health
- **Test Repository:** [github.com/Vamsi-o/action-repo](https://github.com/Vamsi-o/action-repo)

---

## 🎯 Problem Statement

Modern API integrations require reliable webhook processing with visibility into delivery success, failure rates, and performance metrics. This system provides real-time event tracking and production-grade reliability.

---

## 📊 Features

- GitHub webhook receiver (PUSH, PR, MERGE)
- Event validation and parsing
- MongoDB storage with full payloads
- REST API for querying events
- Auto-refreshing dashboard (15s polling)
- Event statistics and timeline
- Production deployment
- CORS configured
- Health monitoring

---

## 🛠️ Tech Stack

**Backend:**

- Python 3.12
- Flask 3.0
- MongoDB Atlas
- Gunicorn

**Frontend:**

- Next.js 14
- TypeScript
- Tailwind CSS
- Framer Motion

**Infrastructure:**

- Leapcell (backend hosting)
- Vercel (frontend hosting)
- MongoDB Atlas (database)

---

## 🏗️ Architecture

![System Architecture](docs/architecture.png)

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed component breakdown.

---

## 📝 Design Decisions

### Why Flask + MongoDB?

- High-throughput event processing
- Flexible schema for varying webhook payloads
- Horizontal scalability for production loads

**Polling (15s) Trade-offs:**

- Simple, reliable, and works everywhere
- Easy to debug and monitor

### Production Considerations

- Deployed on Leapcell (auto-scaling)
- MongoDB Atlas (replica sets, automatic failover)
- CORS configured for multi-origin access
- Structured logging for observability

---

## 🚦 Setup & Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB instance (or MongoDB Atlas)

---

### Backend Setup

```bash
cd Backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI

# Run locally
python run.py
# Server starts on http://localhost:5000
```

---

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local

# Run development server
npm run dev
# Open http://localhost:3000
```

---

### Test Webhook

```bash
curl -X POST http://localhost:5000/webhook \
    -H "Content-Type: application/json" \
    -d '{
        "ref": "refs/heads/main",
        "commits": [{"id": "test", "author": {"name": "Test"}}]
    }'
```

---

## 📸 Screenshot

![Dashboard](docs/screenshot.png)

---

## 📚 Documentation

- [API Documentation](API.md)
- [Architecture Details](ARCHITECTURE.md)

---

## 👤 Author

**Vamshi**

- GitHub: [@Vamsi-o](https://github.com/Vamsi-o)
- Email: iamvamsi0@gmail.com

**Built for TechStaX Technical Assessment | January 2026**
