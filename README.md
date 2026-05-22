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

*To be added once the distribution method is finalized.*

## ⚙️ Configuration

| Variable | Description |
|----------|-------------|
| `YANDEX_API_KEY` | Yandex Cloud service account API key |
| `YANDEX_FOLDER_ID` | Yandex Cloud folder ID |

## 🗺️ Roadmap

- [ ] Automated A/B testing for persona shift validation
- [ ] FastAPI integration for network access
- [ ] Port to ONNX Runtime to reduce image size
- [ ] Unit test coverage for critical components
- [ ] Expand localization (add new languages)

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🙏 Acknowledgements

- [sentence-transformers](https://www.sbert.net/) — embedding models library
- [spaCy](https://spacy.io/) — industrial-strength NLP toolkit
- [KeyBERT](https://maartengr.github.io/KeyBERT/) — keyword extraction
- Yandex Cloud — providing access to DeepSeek V3.2
