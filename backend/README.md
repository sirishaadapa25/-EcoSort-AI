# EcoSort AI – Backend

Flask REST API. Full instructions are in the [project README](../README.md).

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                              # Windows: copy .env.example .env
python app.py                                     # http://localhost:5000
python -m unittest -v                             # run tests
```

- `GET /api/health` – status check
- `POST /api/analyze` – body `{"waste": "banana peel"}`

Without `AI_API_URL` and `AI_MODEL` in `.env`, the API runs in labelled Demo Mode (keyword matching, not AI). Never commit `.env`.
