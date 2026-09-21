# EcoSort AI – Presentation Kit

Screenshots for slide 8 are in `docs/screenshots/`. They were captured in **Demo Mode**. If you connect a real model, retake `3-ai-result.png` and `5-second-example-banana-peel.png` so they show the model name.

---

## 1. PPT content (12 slides)

### Slide 1 – Title
**EcoSort AI**
AI-Powered Waste Segregation and Sustainable Disposal Assistant

Name: Adapa Sirisha
College: Avanthi
1M1B AI for Sustainability Virtual Internship

### Slide 2 – Problem Statement
- People often don't know which bin an item belongs in: organic/wet, recyclable/dry, hazardous, e-waste, or general.
- Wrong segregation can contaminate recyclable material and reduce the effectiveness of waste management.
- This happens in colleges, homes, and communities.
- **How might we use AI to help people correctly identify and segregate waste and provide appropriate disposal guidance so that waste management becomes more sustainable?**

### Slide 3 – SDG Alignment
- **Primary: SDG 12 – Responsible Consumption and Production.** Responsible waste handling, recycling, reuse.
- **Secondary: SDG 13 – Climate Action.** Better waste management is an intended contribution to reducing environmental impact. The project does not claim to solve climate change.

### Slide 4 – Target Users and Existing Gap
- **Who:** students, households, teachers, community members, and anyone who wants basic disposal guidance.
- **Gap:** signage and posters are generic, rules differ by place, and many items are confusing (a used battery, a broken phone, an unlabelled chemical container).
- **Need:** quick, plain-language answers that explain *why*, and that say when the user should check local rules.

### Slide 5 – Proposed Solution
- EcoSort AI is a web-based AI decision-support tool.
- The user describes an item in plain language.
- The system returns: category, recommended action, sustainability tip, explanation, and uncertainty.
- Runs on a normal computer in a browser. No hardware.

### Slide 6 – System Architecture
User → Frontend (HTML/CSS/JS) → Flask REST API (`POST /api/analyze`) → AI model → Classification + Recommendation → Frontend result

Fallback: if the AI is unavailable → labelled Demo Mode (keyword dataset, not AI).

### Slide 7 – AI Elements and Tools
- Model: **[write the model you actually connected, or "AI workflow demonstration – no model connected"]**
- Prompt engineering: fixed system prompt, five allowed categories, "do not invent local rules", uncertainty required.
- Natural-language understanding of free-text descriptions.
- Classification into five categories.
- Recommendation and explanation generation.
- Structured JSON output, validated by the backend.

### Slide 8 – Prototype Screenshots
Insert: `1-homepage.png` (Home), `2-user-input.png` and `3-ai-result.png` (Analyze page), `4-waste-categories.png` (Categories page). The app has five pages: Home, Analyze, Categories, Responsible AI, About.

### Slide 9 – Sample Results
Expected classifications used as the project's test cases:

| Input | Category |
|---|---|
| Banana peel | Organic / Wet Waste |
| Plastic water bottle | Recyclable / Dry Waste |
| Used battery | Hazardous / Special Waste |
| Old mobile phone | E-Waste |
| Cardboard box | Recyclable / Dry Waste |
| Unknown chemical container | Hazardous / Special Waste, with uncertainty |

Each result also shows an action, a tip, an explanation, and an uncertainty note.

### Slide 10 – Responsible AI
- **Fairness:** same approach for every user.
- **Transparency:** explanation with every result; result states whether it came from an AI model or Demo Mode.
- **Privacy:** no personal information requested; inputs not stored.
- **Accuracy:** AI can be wrong; verify with local guidelines.
- **Human oversight:** decision-support tool, not a replacement for official instructions.

### Slide 11 – Expected Impact
- **Social:** helps people learn how to segregate waste and build everyday habits.
- **Environmental (intended):** correct segregation supports recycling and responsible disposal of hazardous items and e-waste.
- Impact has not been measured in this prototype, so no numerical claims are made.

### Slide 12 – Future Scope and Conclusion
- Future: image-based recognition, multilingual support, local waste-management knowledge, RAG over official guidelines, mobile app, analytics.
- Conclusion: AI can make waste-segregation guidance easier to access and easier to understand, as a support for, not a replacement of, local waste-management systems.

---

## 2. Demo script (1–2 minutes)

1. Open EcoSort AI at `http://localhost:5000`, then click **Analyze Waste** to go to the analyzer page.
2. Type **plastic water bottle**.
3. Click **Analyze Waste**.
4. Point to the category: **Recyclable / Dry Waste**. Optionally click **See this category** to show the blue bin on the Categories page, then go back.
5. Read the recommended action.
6. Read the sustainability tip.
7. Type **banana peel** and analyze.
8. Show the different result: **Organic / Wet Waste**.
9. Say: "This is a decision-support tool. It shows uncertainty and tells users to check local rules."
10. Say: "It supports SDG 12, Responsible Consumption and Production."

If a Demo Mode banner is visible, say so: "The AI service isn't connected in this run, so this result comes from a small built-in dataset. With a model connected, the same interface shows the model's answer."

---

## 3. Short explanation for your mentor or evaluator

"Many people don't know which bin an item goes in, and wrong segregation can contaminate recyclables. EcoSort AI is a web app where you type an item, like 'used battery', and it tells you the waste category, how to dispose of it, a sustainability tip, and why. The frontend is HTML, CSS, and JavaScript. It calls a Flask REST API, which sends the description to a language model with a prompt that restricts it to five categories and tells it not to invent local rules. The backend checks the model's answer before showing it. If the AI isn't available, the app switches to a clearly labelled demo mode instead of pretending. It supports SDG 12, and the environmental benefit is an intended contribution, not something I measured. It's a decision-support tool, and users should always verify local rules."

Likely questions:
- **Which AI did you use?** Answer with what is true: the model in your `.env`, or "no model connected; this is a workflow demonstration in Demo Mode".
- **Is it always right?** No. That's why every result has an uncertainty note and the app tells users to check local guidelines.
- **What about privacy?** It doesn't ask for personal information, and the backend doesn't store or log what users type.
- **What would you add next?** Local rules through RAG, multiple languages, and image input.

---

## 4. Project description for submission

EcoSort AI is a software-based AI sustainability assistant designed to help users identify appropriate waste categories and understand responsible disposal practices. The system uses natural-language AI to analyze waste descriptions, classify them into relevant categories, and provide disposal recommendations and sustainability tips. The project primarily supports SDG 12 – Responsible Consumption and Production and demonstrates how responsible AI can be applied to everyday environmental challenges.

---

## 5. Order of work before the deadline

1. Run the backend and tests.
2. Open the frontend and try the six test items.
3. Decide: connect a model, or present as Demo Mode. Update the "Which AI is actually used?" section in `README.md` and slide 7.
4. Retake screenshots if needed.
5. Build the PPT/PDF from section 1.
6. Push to GitHub. Check that `.env` is not included.
