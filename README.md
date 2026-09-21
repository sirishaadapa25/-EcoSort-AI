# EcoSort AI – AI-Powered Waste Segregation and Sustainable Disposal Assistant

Software-only prototype built for the **1M1B AI for Sustainability Virtual Internship** (with IBM SkillsBuild and AICTE).

A user types a waste item in plain language. EcoSort AI returns the waste category, how to dispose of it, a sustainability tip, a short explanation, and what it is unsure about.

## Problem Statement

Improper waste segregation is common in colleges, homes, and communities. People often don't know whether an item belongs in organic/wet, recyclable/dry, hazardous, e-waste, or general waste. Wrong segregation can contaminate recyclable material and make waste management less effective.

> How might we use AI to help people correctly identify and segregate waste and provide appropriate disposal guidance so that waste management becomes more sustainable?

## SDG Alignment

- **Primary: SDG 12 – Responsible Consumption and Production.** Supports responsible waste handling, recycling, reuse, and sustainable consumption.
- **Secondary: SDG 13 – Climate Action.** Better waste management and responsible resource use are intended to contribute to reducing environmental impact. This project does not claim to solve climate change.

## Target Users

Students, households, teachers, and community members who want basic disposal guidance, including users with limited technical knowledge.

## Solution

```
User → Frontend (HTML/CSS/JS) → Flask REST API → AI model → Category + guidance → Frontend result
```

1. The user enters a waste description.
2. The frontend sends `POST /api/analyze`.
3. The backend validates the input and sends it, with the EcoSort system prompt, to the configured AI model.
4. The backend validates the model's JSON answer and returns a structured response.
5. The frontend shows the result, with a link to the matching bin on the Categories page.

## AI Elements

- **Generative AI / LLM:** understands the description and writes the guidance.
- **Prompt engineering:** a fixed system prompt (see `SYSTEM_PROMPT` in `backend/app.py`) restricts the model to five categories, forbids inventing local rules, and asks for uncertainty.
- **Natural-language understanding:** free-text input such as "old mobile phone" or "used plastic water bottle".
- **Classification:** Organic / Wet, Recyclable / Dry, Hazardous / Special, E-Waste, General / Residual.
- **Recommendation generation:** recommended action, sustainability tip, explanation, uncertainty.
- **Structured output:** the model must answer in JSON. The backend checks the category is one of the five and that the required fields exist. Otherwise it treats the answer as invalid.

### Which AI is actually used? (fill this in before submitting)

The backend calls any **OpenAI-compatible chat-completions endpoint** you configure in `.env`. Write the truth here:

- [ ] Connected model: `__________` (for example an IBM Granite model served locally with Ollama)
- [ ] No AI connected: the project runs in **Demo Mode** only and should be presented as an AI *workflow* demonstration.

IBM watsonx.ai uses its own authentication and request format, so it is **not** built in. Do not say IBM Granite was used unless the connected model really is a Granite model.

### Demo Mode (fallback)

If no AI service is configured, or it times out, errors, or returns unusable output, the backend answers from a small built-in keyword dataset (plastic bottle, banana peel, cardboard, battery, mobile phone, food waste, glass bottle, broken glass, chemical container). Every such result is labelled **"Demo Mode – AI service unavailable"** and states that it is keyword matching, not an AI model.

## Technology

| Layer | Tools |
|---|---|
| Frontend | HTML5, CSS3, JavaScript (`fetch`) |
| Backend | Python, Flask, REST API |
| AI | Any OpenAI-compatible LLM endpoint (for example IBM Granite via Ollama), prompt engineering, structured JSON output |
| Development | VS Code, GitHub |

No hardware, sensors, cameras, or IoT devices are used.

## Project Structure

```
EcoSort-AI/
├── frontend/
│   ├── index.html            (Home)
│   ├── analyze.html          (waste analyzer)
│   ├── categories.html       (five waste categories)
│   ├── responsible-ai.html
│   ├── about.html            (problem, SDGs, approach)
│   ├── style.css
│   └── script.js             (used by analyze.html)
├── backend/
│   ├── app.py
│   ├── test_app.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── docs/
│   ├── PRESENTATION_KIT.md      (slide content, demo script, talking points)
│   └── screenshots/             (Demo Mode screenshots)
├── .gitignore
└── README.md
```

## Run Locally

Requires Python 3.9+.

**Windows (PowerShell)**
```powershell
cd EcoSort-AI\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

**macOS / Linux**
```bash
cd EcoSort-AI/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Then open **http://localhost:5000** in your browser. The Flask server also serves the frontend, so nothing else is needed. (Opening `frontend/index.html` directly also works while the backend is running.)

Pages: Home (`/`), Analyze (`/analyze.html`), Categories (`/categories.html`), Responsible AI (`/responsible-ai.html`), About (`/about.html`).

With an empty `.env`, the app runs in Demo Mode.

### Connect a real AI model (optional)

Example with a local IBM Granite model through [Ollama](https://ollama.com), no API key needed:

```bash
ollama pull granite3.3:2b      # check the exact tag in the Ollama library
```

Then set these in `backend/.env` and restart `python app.py`:

```
AI_API_URL=http://localhost:11434/v1/chat/completions
AI_MODEL=granite3.3:2b
```

For a hosted OpenAI-compatible service, set `AI_API_URL`, `AI_MODEL`, and `AI_API_KEY`. Check `http://localhost:5000/api/health`: it shows `"mode": "ai"` when a model is configured. Each result also shows whether it came from the AI model or Demo Mode.

## API

**GET `/api/health`**
```json
{ "status": "EcoSort AI backend is running", "mode": "demo" }
```

**POST `/api/analyze`**
```json
{ "waste": "used plastic bottle" }
```
Response (`200`):
```json
{
  "success": true,
  "item": "used plastic bottle",
  "category": "Recyclable / Dry Waste",
  "action": "...",
  "tip": "...",
  "explanation": "...",
  "uncertainty": "...",
  "mode": "ai",
  "model": "granite3.3:2b",
  "needs_more_info": false
}
```
In Demo Mode, `mode` is `"demo"` and the response includes `mode_label` and `notice` instead of `model`.

Errors return `{ "success": false, "error": "..." }` with status `400` (empty or invalid input), `404`, `405`, `413` (too large), `429` (too many requests), or `500`. For unclear items the response has `category: "Needs more information"` and:

> I need more information to classify this item accurately. Please provide a clearer description and check your local waste-management guidelines.

## Testing

```bash
cd backend
python -m unittest -v
```

The tests cover the six sample cases (banana peel, plastic water bottle, used battery, old mobile phone, cardboard box, unknown chemical container), empty and invalid input, oversized requests, rate limiting, and the AI path (timeout, HTTP error, invalid output, fallback). **The AI path is tested with a mocked HTTP response, not a real model.** Test your connected model manually with the same six items.

## Error Handling

Empty input, invalid requests, backend unavailable, AI unavailable, AI timeout, invalid AI response, and unknown items are all handled with friendly messages in the UI. If the AI fails, the backend falls back to Demo Mode instead of showing a blank screen.

## Security

- API keys live only in `.env`, which is listed in `.gitignore`. **Never commit `.env`.**
- Input is validated (type, length, control characters) and the request body size is capped.
- Results are rendered with `textContent`, so model output cannot inject HTML.
- Basic per-IP rate limit; security headers on served pages.
- User input is not logged or stored.

## Responsible AI

- **Fairness:** every description is analyzed the same way, regardless of the user.
- **Transparency:** results include an explanation and say whether they came from an AI model or Demo Mode.
- **Privacy:** no personal or sensitive information is requested, and inputs are not stored.
- **Accuracy:** AI output may be wrong. Users should verify rules with local authorities or official guidelines.
- **Human oversight:** EcoSort AI is a decision-support and awareness tool. It does not replace official waste-management instructions.
- **Environmental responsibility:** no unsupported claims about the environmental impact of specific disposal methods.

## Future Scope

- Image-based waste recognition
- Multilingual support
- Local waste-management knowledge
- Retrieval-augmented generation (RAG) over official local guidelines
- Mobile application
- Usage analytics (privacy-preserving)
