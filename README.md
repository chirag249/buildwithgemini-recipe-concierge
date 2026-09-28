# 🍳 Recipe Concierge

A conversational culinary AI assistant designed to help home cooks discover, personalize, scale, and visualize recipes while strictly respecting dietary preferences and allergies across sessions. Built with **Google ADK (Agent Development Kit)**, **Vertex AI Agent Engine**, **Cloud Firestore**, and **Google Cloud Storage**.

![Recipe Concierge Demo](./demo.gif)

---

## ✨ Implemented Capabilities & Architecture

Recipe Concierge integrates key Google Agent Platform and Google Cloud services:

* **🧠 Cross-Session Long-Term Memory (Vertex AI Memory Bank)**
  * Uses `VertexAiMemoryBankService` and `PreloadMemoryTool` to persist user dietary restrictions, allergies (e.g., peanuts, gluten, dairy), and favorite cuisines across chat sessions.
  * Automatically inspects preloaded memories on every conversation turn to eliminate allergen recommendations.

* **🍲 Recipe Catalog & Database Management (Cloud Firestore)**
  * `search_recipes`: Queries Firestore for matching dishes and ingredients.
  * `get_recipe_details`: Fetches full ingredient breakdowns and step-by-step cooking instructions.
  * `add_recipe`: Persists new custom recipes directly to the Firestore collection.
  * `generate_grocery_shopping_list`: Aggregates ingredients into organized shopping lists.

* **🎨 Visual Recipe Generation (Gemini 3.1 Flash-Lite Image & Cloud Storage)**
  * `generate_recipe_image`: Generates dish photos using `gemini-3.1-flash-lite-image` in the `global` region.
  * Saves image artifacts to the local playground and uploads image bytes directly to a public Cloud Storage bucket (`gs://recipe-concierge-media-...`), returning public `https://storage.googleapis.com/...` URLs.

* **🎴 Rich Card UI Rendering (A2UI v0.8)**
  * Generates native structured UI cards (headers, recipe cards, columns, and embedded images) using `A2uiSchemaManager` (version 0.8) and `BasicCatalog`.
  * Wires responses via `a2ui_callback` to render cards both in ADK Web and in custom web frontends.

* **⚡ Code Execution Sandbox (Agent Engine Sandbox)**
  * `AgentEngineSandboxCodeExecutor`: Safely executes Python code inside an isolated sandbox to handle nutritional calculations, recipe scaling for varying serving sizes, and unit conversions.

* **📍 Location & External APIs**
  * `find_nearby_places` & `geocode_address`: Uses Google Maps APIs to find nearby grocery stores, specialty markets, and bakeries.
  * `search_online_recipes`: Fetches external recipe inspiration.

---

## 🔮 Planned Capabilities

* **🎬 Short Recipe Video Generation**: Integration with Google Omni models (`gemini-omni-flash-preview`) via the Interactions API to generate short step-by-step cooking videos *(planned, not yet fully integrated)*.

---

## 🛠️ Local Setup & Execution Instructions

### Prerequisites
* Python 3.11+
* Google Cloud SDK (`gcloud`) authenticated with Application Default Credentials (`gcloud auth application-default login`)

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run the Local ADK Playground
To launch the agent playground with long-term memory support:
```bash
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<AGENT_ENGINE_ID>
```

### 3. Run the Frontend Proxy & Chat UI
To run the minimal FastAPI A2A proxy server and chat frontend locally:
```bash
cd frontend
uv pip install -r requirements.txt
AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>" \
AGENT_DIRECTORY="app" \
PORT=8080 \
uv run python main.py
```

### 4. Deploy to Agent Platform
To deploy the agent to Google Cloud Agent Runtime:
```bash
agents-cli deploy --update-env-vars GOOGLE_MAPS_API_KEY=<YOUR_API_KEY>
```

---

## 📁 Repository Structure

```
├── app/
│   ├── agent.py              # Root agent definition, instructions, callbacks & tool wiring
│   ├── firestore_tools.py    # Firestore database CRUD tools
│   ├── image_tools.py        # Gemini image generation & GCS upload tool
│   ├── maps_tools.py         # Google Maps geocoding & nearby places tools
│   ├── online_api_tools.py   # External recipe search tools
│   └── a2ui_utils.py         # A2UI card renderer callback
├── frontend/
│   ├── main.py               # FastAPI A2A proxy server
│   ├── requirements.txt      # Frontend Python dependencies
│   └── static/
│       └── index.html        # Custom chat interface with A2UI card renderer
├── demo.gif                  # Inline looping demo recording
├── agents-cli-manifest.yaml  # Agent deployment manifest
├── pyproject.toml            # Project dependencies & packaging
└── README.md                 # Project documentation
```
