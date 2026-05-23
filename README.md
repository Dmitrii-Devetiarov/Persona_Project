# Latent Persona Memory

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

> An LLM wrapper that gives your assistant a persistent persona — carrying conversation style and context across dialogs. The persona is shaped not by what the model knows, but by how the user writes: brevity, emotional tone, dryness, and more. Memory is fuzzy — it pulls only the gist from past conversations, not the raw text.

## 🖥️ Interface

### Main view
Key controls are on the sidebar (scrollable).
![General View](screenshots/General_view.png)

### Mode panel
![Mode Panel](screenshots/Mode_panel.png)

### Manual axis sliders
![Manual Sliders](screenshots/Manual_sliders.png)

### Additional system prompt settings
![Additional System Prompt](screenshots/Additional_system_prompt_par.png)

### Persona file controls
![Persona Control](screenshots/Persona_control.png)

### Context window remaining indicator
![Context Indicator](screenshots/Context_indicator.png)

### Reset current dialogue
![Dialog Reset](screenshots/Dialoge_reset.png)


## ✨ Features

- **Streaming style analysis:** Automatic detection of 20 linguistic surface features
- **Semantic memory:** Retains conversation context without storing raw facts or transcripts
- **Adaptive behavior:** The model adjusts to your communication style along 8 independent axes
- **Fully containerized:** One-click Docker launch, all dependencies included
- **Fine-grained control:** Manual tuning of every persona parameter through the UI, with support for custom user instructions as an additional system prompt section
- **Bilingual:** Full Russian and English support — UI, marker detection, and prompts

## 🏗️ Architecture

The project runs four parallel analysis streams that converge in the Persona Core to produce the final system prompt for the LLM. All components are bilingual — stop-word detection, style markers, and prompts work in both Russian and English.

| Stream | Purpose | Method |
|--------|---------|--------|
| **A — Fuzzy Memory** | Semantic cloud of past dialogues | E5-large + KeyBERT + associative memory |
| **B — Surface Style** | Linguistic surface features | spaCy + pymorphy3 (20 features) |
| **C1 — Explicit** | Direct user instructions | Prototype embeddings, 8 axes |
| **C2 — Implicit** | Reactions to model responses | Follow-up message analysis |
| **Fusion** | Merging the streams | Adaptive weights, 8 axes |

### Persona axes

| Axis | Range | Description |
|------|-------|-------------|
| `emotionality` | –1 (dry) ↔ +1 (empathetic) | Level of emotional engagement |
| `factual_accuracy` | –1 (broadest possible view) ↔ +1 (deep dive into the most accepted version) | Breadth of perspectives vs. depth of consensus |
| `verbosity` | –1 (concise) ↔ +1 (detailed) | Response length and level of detail |
| `figurativeness` | –1 (plain speech) ↔ +1 (literary, figurative) | Richness and complexity of expressive language |
| `disagreement` | –1 (agreeable) ↔ +1 (debate-oriented) | Willingness to challenge and object |
| `comfort` | –1 (overly familiar) ↔ +1 (formal politeness) | Social distance and formality |
| `model_resistance` | 0 (yield to user pressure) ↔ +1 (hold the line) | Resilience to user pressure and role imposition |
| `complexity` | –1 (simple) ↔ +1 (terminology-heavy) | Technical complexity of language |

## 🚀 Quick start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your machine
- Yandex Cloud API key with access to DeepSeek

### Option 1: Build from source

```bash
# Clone the repository
git clone https://github.com/Dmitrii-Devetiarov/Persona_Project.git
cd Persona_Project

# Set up environment
cp .env.example .env
# Edit .env with your YANDEX_API_KEY and YANDEX_FOLDER_ID (see Configuration)

# Download and prepare the E5-large model
# Option A: Download the full model and trim it (requires ~9 GB temporarily)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-large')"
# Then copy only the required files to models/e5-large-lite/ (see structure below)

# Option B: Manually create models/e5-large-lite/ with the following files:
#   model.safetensors, tokenizer.json, sentencepiece.bpe.model,
#   tokenizer_config.json, special_tokens_map.json, config.json,
#   modules.json, sentence_bert_config.json, 1_Pooling/config.json

# Build and run
docker compose up
```
Open http://localhost:8501 in your browser.

### Option 2: Pull from GitHub Container Registry

```bash
# Pull the latest image
docker pull ghcr.io/dmitrii-devetiarov/persona-project:latest

# Create a project directory and navigate into it
mkdir persona-memory && cd persona-memory

#Create a file named docker-compose.yml with the following content:
services:
  persona:
    image: ghcr.io/dmitrii-devetiarov/persona-project:latest
    pull_policy: always
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped

# Create .env file with your Yandex Cloud API keys (see Configuration)

# Create empty data directory for persona persistence
mkdir -p data

# Start the application
docker compose up
```
Open http://localhost:8501 in your browser.



## ⚙️ Configuration

| Variable | Description |
|----------|-------------|
| `YANDEX_API_KEY` | Yandex Cloud service account API key |
| `YANDEX_FOLDER_ID` | Yandex Cloud folder ID |

Note on the model: The models/e5-large-lite/ folder contains a trimmed version of intfloat/multilingual-e5-large. It excludes pytorch_model.bin, onnx/, openvino/, and other non-essential files, keeping only what sentence-transformers needs to run. This reduces the size from ~9 GB to ~2.2 GB. The model is fully functional.

Required file structure for models/e5-large-lite/:

models/e5-large-lite/
├── model.safetensors
├── tokenizer.json
├── sentencepiece.bpe.model
├── tokenizer_config.json
├── special_tokens_map.json
├── config.json
├── modules.json
├── sentence_bert_config.json
└── 1_Pooling/
    └── config.json
    
## 🗺️ Roadmap

- [ ] Automated A/B testing for persona shift validation
- [ ] FastAPI integration for network access
- [ ] Port to ONNX Runtime to reduce image size
- [ ] Unit test coverage for critical components
- [ ] Expand localization (add new languages)

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Third-party licenses

This project uses the following open-source libraries, distributed under their respective licenses:

| Library | License |
|---------|---------|
| **sentence-transformers** (Nils Reimers) | [Apache 2.0](https://github.com/UKPLab/sentence-transformers/blob/master/LICENSE) |
| **Streamlit** | [Apache 2.0](https://github.com/streamlit/streamlit/blob/develop/LICENSE) |
| **OpenAI Python SDK** | [Apache 2.0](https://github.com/openai/openai-python/blob/master/LICENSE) |
| **KeyBERT**, **spaCy**, **pymorphy3**, **tiktoken** | MIT |
| **scikit-learn**, **numpy** | BSD 3-Clause |

Full license texts for **Apache 2.0** components are provided in the [`third-party/`](third-party/) directory.

## 🙏 Acknowledgements

Special thanks to the creators and maintainers of **sentence-transformers**, **spaCy**, **KeyBERT**, and **Streamlit** — your work made this project possible.

Grateful to **Yandex Cloud** for providing access to DeepSeek.

And a sincere thank you to the entire open-source community and all contributors to the libraries this project depends on — the ones listed above and the many others not named but relied upon.