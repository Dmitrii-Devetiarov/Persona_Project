# ui/streamlit_app.py — полный файл с индикатором контекста и галками сохранения
"""Streamlit UI for Latent Persona Memory MVP — full version with controls."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
import os
import time

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.locales import EN, RU 
from src.persona_manager import PersonaManager

load_dotenv()

# ============================================================
# Language
# ============================================================
if "lang" not in st.session_state:
    st.session_state.lang = "en"

L = {"ru": RU, "en": EN}[st.session_state.lang]

# ============================================================
# Page config
# ============================================================
st.set_page_config(page_title=L["title"], page_icon="🧠", layout="centered")

st.title(L["title"])
st.caption(L["subtitle"])


# ============================================================
# Cached manager and client
# ============================================================
@st.cache_resource
def get_manager() -> PersonaManager:
    return PersonaManager(persist=True)


manager = get_manager()


@st.cache_resource
def get_client():
    api_key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    if not api_key or not folder_id:
        st.error(L["error_no_keys"])
        st.stop()
    return OpenAI(
        api_key=api_key,
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=folder_id,
    )


client = get_client()

# ============================================================
# Token counter
# ============================================================
MODEL_MAX_TOKENS = 1000000
WARNING_THRESHOLD = 0.2

try:
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")

    def count_tokens(messages: list[dict]) -> int:
        total = 0
        for msg in messages:
            total += len(enc.encode(msg["content"])) + 4
        return total

except ImportError:

    def count_tokens(messages: list[dict]) -> int:
        # Approximation: Russian ~1.5 tokens per word, English ~ 1.3
        ratio = 1.5 if st.session_state.lang == "ru" else 1.3
        total = 0
        for msg in messages:
            total += int(len(msg["content"].split()) * ratio) + 4
        return total


# ============================================================
# Init session state
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "auto"
if "manual_prefs" not in st.session_state:
    st.session_state.manual_prefs = {}
if "enabled_axes" not in st.session_state:
    st.session_state.enabled_axes = {
        "emotionality": True,
        "factual_accuracy": True,
        "verbosity": True,
        "figurativeness": True,
        "disagreement": True,
        "comfort": True,
        "model_resistance": True,
        "complexity": True,
    }
if "update_persona" not in st.session_state:
    st.session_state.update_persona = True
if "selected_messages" not in st.session_state:
    st.session_state.selected_messages = set()
if "user_instruction" not in st.session_state:
    st.session_state.user_instruction = ""


# ============================================================
# Helpers
# ============================================================
def axis_color(value: float) -> str:
    if value > 0.2:
        return "#FF8C00"
    elif value < -0.2:
        return "#4A90D9"
    else:
        return "#9E9E9E"


def save_persona_to_file(name: str):
    safe_name = "".join(c for c in name if c.isalnum() or c in "_-")
    if not safe_name:
        raise ValueError("Invalid persona name")
    personas_dir = PROJECT_ROOT / "data" / "personas"
    personas_dir.mkdir(parents=True, exist_ok=True)
    prefs = (
        st.session_state.manual_prefs
        if st.session_state.mode == "manual"
        else manager.preferences
    )
    persona_data = {
        "name": safe_name,
        "mode": st.session_state.mode,
        "preferences": prefs,
        "enabled_axes": st.session_state.enabled_axes,
    }
    filepath = personas_dir / f"{safe_name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(persona_data, f, ensure_ascii=False, indent=2)
    return filepath


def load_persona_from_file(filepath: Path) -> dict:
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def context_indicator(pct: float) -> str:
    circles = []
    for i in range(5):
        threshold = (i + 1) / 5
        if pct >= threshold:
            if i == 0:
                color = "#F44336"
            elif i <= 2:
                color = "#FFC107"
            else:
                color = "#4CAF50"
            circles.append(
                f'<span style="color:{color}; font-size:22px; margin:0 3px; '
                f'text-shadow: 0 0 8px {color};">●</span>'
            )
        else:
            if i == 0:
                color = "#8B0000"
            elif i <= 2:
                color = "#9E9D24"
            else:
                color = "#2E7D32"
            circles.append(
                f'<span style="color:{color}; font-size:22px; margin:0 3px;">●</span>'
            )
    return "".join(circles)


# ============================================================
# Axis labels (from locales)
# ============================================================
AXIS_CHOICES = {
    "emotionality": [
        (-1.0, L["emotionality_label_m2"]),
        (-0.5, L["emotionality_label_m1"]),
        (0.0, L["emotionality_label_0"]),
        (0.5, L["emotionality_label_p1"]),
        (1.0, L["emotionality_label_p2"]),
    ],
    "factual_accuracy": [
        (-1.0, L["factual_label_m2"]),
        (-0.5, L["factual_label_m1"]),
        (0.0, L["factual_label_0"]),
        (0.5, L["factual_label_p1"]),
        (1.0, L["factual_label_p2"]),
    ],
    "verbosity": [
        (-1.0, L["verbosity_label_m2"]),
        (-0.5, L["verbosity_label_m1"]),
        (0.0, L["verbosity_label_0"]),
        (0.5, L["verbosity_label_p1"]),
        (1.0, L["verbosity_label_p2"]),
    ],
    "figurativeness": [
        (-1.0, L["figurativeness_label_m2"]),
        (-0.5, L["figurativeness_label_m1"]),
        (0.0, L["figurativeness_label_0"]),
        (0.5, L["figurativeness_label_p1"]),
        (1.0, L["figurativeness_label_p2"]),
    ],
    "disagreement": [
        (-1.0, L["disagreement_label_m2"]),
        (-0.5, L["disagreement_label_m1"]),
        (0.0, L["disagreement_label_0"]),
        (0.5, L["disagreement_label_p1"]),
        (1.0, L["disagreement_label_p2"]),
    ],
    "comfort": [
        (-1.0, L["comfort_label_m2"]),
        (-0.5, L["comfort_label_m1"]),
        (0.0, L["comfort_label_0"]),
        (0.5, L["comfort_label_p1"]),
        (1.0, L["comfort_label_p2"]),
    ],
    "model_resistance": [
        (0.0, L["model_resistance_label_0"]),
        (0.3, L["model_resistance_label_1"]),
        (0.6, L["model_resistance_label_2"]),
        (0.9, L["model_resistance_label_3"]),
    ],
    "complexity": [
        (-1.0, L["complexity_label_m2"]),
        (-0.5, L["complexity_label_m1"]),
        (0.0, L["complexity_label_0"]),
        (0.5, L["complexity_label_p1"]),
        (1.0, L["complexity_label_p2"]),
    ],
}

all_axes = [
    "emotionality",
    "factual_accuracy",
    "verbosity",
    "figurativeness",
    "disagreement",
    "comfort",
    "model_resistance",
    "complexity",
]

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    # Language selector
    lang = st.selectbox(
        "Language / Язык",
        options=["ru", "en"],
        index=0 if st.session_state.lang == "ru" else 1,
        key="lang_selector",
    )
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()

    st.divider()

    st.subheader(L["persona_section"])

    prefs = manager.preferences

    if any(abs(v) > 0.01 for v in prefs.values()):
        for axis, value in prefs.items():
            color = axis_color(value)
            st.markdown(
                f'<span style="color:{color}; font-size:18px;">●</span> '
                f"{axis}: {value:+.3f}",
                unsafe_allow_html=True,
            )
    else:
        st.caption(L["no_data"])

    memory_size = len(manager.keyword_memory.memory)
    st.metric(L["memory_metric"], memory_size)

    # === Индикатор контекста ===
    st.divider()
    st.subheader(L["context_section"])
    current_tokens = count_tokens(st.session_state.messages)
    remaining_pct = 1.0 - (current_tokens / MODEL_MAX_TOKENS)
    remaining_abs = max(0, MODEL_MAX_TOKENS - current_tokens)

    st.metric(
        L["context_remaining"],
        f"{remaining_pct:.0%}",
        delta=f"~{remaining_abs:,} tokens",
        delta_color="off",
    )
    st.markdown(context_indicator(remaining_pct), unsafe_allow_html=True)

    if remaining_pct < WARNING_THRESHOLD:
        st.warning(L["context_warning"])

    st.divider()

    # === Режим ===
    st.subheader(L["mode_section"])
    mode = st.radio(
        L["mode_section"],
        options=["auto", "manual", "intact"],
        format_func=lambda x: {
            "auto": L["mode_auto"],
            "manual": L["mode_manual"],
            "intact": L["mode_intact"],
        }[x],
        index=["auto", "manual", "intact"].index(st.session_state.mode),
        label_visibility="collapsed",
    )
    st.session_state.mode = mode

    # === Обновление персоны ===
    st.session_state.update_persona = st.checkbox(
        L["update_persona_label"],
        value=st.session_state.update_persona,
        help=L["update_persona_help"],
    )

    # --- Флаги памяти ---
    use_memory = st.session_state.get("use_memory", True)
    update_memory = st.session_state.get("update_memory", True)

    st.checkbox(
        L["use_memory_label"],
        value=use_memory,
        key="use_memory",
        help=L["use_memory_help"],
    )
    st.checkbox(
        L["update_memory_label"],
        value=update_memory,
        key="update_memory",
        help=L["update_memory_help"],
    )

    # === Пользовательская ремарка ===
    st.divider()
    st.subheader(L["user_instruction_label"])
    st.session_state.user_instruction = st.text_area(
        L["user_instruction_label"],
        value=st.session_state.user_instruction,
        placeholder=L["user_instruction_placeholder"],
        help=L["user_instruction_help"],
        max_chars=300,
        label_visibility="collapsed",
        key="user_instruction_input",
    )

    # === Активные оси ===
    st.divider()
    st.subheader(L["active_axes"])
    cols = st.columns(2)
    for i, axis in enumerate(all_axes):
        with cols[i % 2]:
            st.session_state.enabled_axes[axis] = st.checkbox(
                axis, value=st.session_state.enabled_axes[axis], key=f"enable_{axis}"
            )

    # === Ручные ползунки ===
    if mode == "manual":
        st.subheader(L["manual_axes"])
        manual_prefs = {}
        for axis in all_axes:
            if not st.session_state.enabled_axes[axis]:
                manual_prefs[axis] = 0.0
                continue
            choices = AXIS_CHOICES[axis]
            labels = [label for _, label in choices]
            values = [val for val, _ in choices]
            current_val = st.session_state.manual_prefs.get(
                axis, manager.preferences.get(axis, 0.0)
            )
            nearest_idx = min(
                range(len(values)), key=lambda i: abs(values[i] - current_val)
            )
            selected_label = st.select_slider(
                label=axis,
                options=labels,
                value=labels[nearest_idx],
                key=f"slider_{axis}",
                label_visibility="visible",
            )
            selected_val = values[labels.index(selected_label)]
            manual_prefs[axis] = selected_val
        st.session_state.manual_prefs = manual_prefs

    st.divider()

    # === Сохранение/загрузка персоны ===
    st.subheader(L["save_persona"])
    persona_name = st.text_input(
        L["persona_name_placeholder"], placeholder=L["persona_name_placeholder"]
    )
    if st.button(L["save_persona_button"]):
        if persona_name.strip():
            filepath = save_persona_to_file(persona_name.strip())
            st.success(f"{L['success_persona_saved']} {filepath.name}")
        else:
            st.warning(L["warning_no_name"])

    personas_dir = PROJECT_ROOT / "data" / "personas"
    if personas_dir.exists():
        saved_personas = list(personas_dir.glob("*.json"))
        if saved_personas:
            persona_names = [p.stem for p in saved_personas]
            selected_persona = st.selectbox(
                L["load_persona"], options=[""] + persona_names
            )
            if selected_persona:
                filepath = personas_dir / f"{selected_persona}.json"
                persona_data = load_persona_from_file(filepath)
                if st.button(f"{L['load_persona_button']} '{selected_persona}'"):
                    st.session_state.manual_prefs = persona_data.get("preferences", {})
                    st.session_state.enabled_axes = persona_data.get(
                        "enabled_axes", st.session_state.enabled_axes
                    )
                    if persona_data.get("mode"):
                        st.session_state.mode = persona_data["mode"]
                    st.success(f"{L['success_persona_loaded']} '{selected_persona}'")
                    st.rerun()

    st.divider()

    # === Обучение ===
    st.subheader(L["train_section"])
    uploaded_dialogs = st.file_uploader(
        L["train_uploader"],
        type="json",
        accept_multiple_files=True,
        help=L["train_uploader"],
    )
    if uploaded_dialogs:
        if st.button(L["train_button"]):
            success_count = 0
            for uploaded_file in uploaded_dialogs:
                try:
                    dialog_data = json.load(uploaded_file)
                    messages = dialog_data.get("messages", [])
                    if messages:
                        manager.update_after_dialog(messages, update_memory)
                        success_count += 1
                except Exception as e:
                    st.error(f"{L['error_persona_update']} {uploaded_file.name}: {e}")
            if success_count > 0:
                st.success(f"{L['train_success']} {success_count}")

    st.divider()

    # === Очистка ===
    if st.button(L["clear_dialog"]):
        st.session_state.messages = []
        st.session_state.selected_messages = set()
        st.rerun()

# ============================================================
# Chat display
# ============================================================
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

    checked = i in st.session_state.selected_messages
    key = f"select_{i}"

    checked_new = st.checkbox("", value=checked, key=key)

    if checked_new:
        st.session_state.selected_messages.add(i)
    else:
        st.session_state.selected_messages.discard(i)


# ============================================================
# Get effective prompt
# ============================================================
def get_effective_prompt(user_input: str) -> str:
    mode = st.session_state.mode
    enabled = st.session_state.enabled_axes
    prompt = ""

    if mode == "intact":
        prompt = ""
    elif mode == "manual":
        prefs = st.session_state.manual_prefs
        parts = []
        for axis in all_axes:
            if not enabled.get(axis, True):
                continue
            value = prefs.get(axis, 0.0)
            label = manager._get_label(axis, value, lang=st.session_state.lang)
            parts.append(f"- {label}")
        if parts:
            prompt = (
                f"{L.get('prompt_frame_manual', '[Style instructions — manual]')}\n"
                + "\n".join(parts)
                + f"\n{L['prompt_frame_close']}"
            )
    else:  # auto
        is_first = len(st.session_state.messages) == 0
        if is_first:
            prompt = manager.get_persona_prompt(
                current_question=user_input, lang=st.session_state.lang
            )
        else:
            prompt = manager.get_persona_prompt(lang=st.session_state.lang)
        if prompt:
            lines = prompt.split("\n")
            filtered_lines = []
            for line in lines:
                if line.startswith("- "):
                    include = True
                    for axis in enabled:
                        if not enabled[axis]:
                            label = manager._get_label(
                                axis,
                                manager.preferences.get(axis, 0.0),
                                lang=st.session_state.lang,
                            )
                            if label in line:
                                include = False
                                break
                    if include:
                        filtered_lines.append(line)
                else:
                    filtered_lines.append(line)
            prompt = "\n".join(filtered_lines)

    # Добавляем пользовательскую инструкцию (для всех режимов)
    user_instruction = st.session_state.get("user_instruction", "").strip()
    if user_instruction:
        instruction_line = f"{L['user_instruction_frame']}"
        f"{user_instruction}"
        f"{L['user_instruction_frame_close']}"
        if prompt and L["prompt_frame_close"] in prompt:
            prompt = prompt.replace(
                L["prompt_frame_close"],
                f"{instruction_line}\n{L['prompt_frame_close']}",
            )
        elif prompt:
            prompt = prompt + "\n" + instruction_line
        else:
            prompt = instruction_line

    return prompt


# ============================================================
# Chat input
# ============================================================
if user_input := st.chat_input(L["chat_input_placeholder"]):
    with st.chat_message("user"):
        st.write(user_input)

    prompt = get_effective_prompt(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write(L["generating"])

    api_messages = []
    if prompt:
        api_messages.append({"role": "system", "content": prompt})
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
    api_messages.append({"role": "user", "content": user_input})
    folder_id = os.getenv("YANDEX_FOLDER_ID")

    try:
        response = client.chat.completions.create(
            model=f"gpt://{folder_id}/deepseek-v4-flash/latest" ,
            temperature=0.5,
            messages=api_messages,
            max_tokens=100000,
            reasoning_effort = None,
            stream=True,
        )
        reply = ""
        for chunk in response:
            try:
                token = chunk.choices[0].delta.content
                if token:
                    reply += token
                    placeholder.write(reply + "▌")
            except (IndexError, AttributeError):
                continue
    except Exception as e:
        reply = f"{L['error_api']} {e}"

    placeholder.write(reply)

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": reply})

    if st.session_state.mode == "auto" and st.session_state.update_persona:
        try:
            manager.update_after_dialog(st.session_state.messages)
        except Exception as e:
            st.error(f"{L['error_persona_update']} {e}")

    st.rerun()

# ============================================================
# Dialog save/load at bottom
# ============================================================
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(L["save_selected"]):
        if st.session_state.selected_messages:
            selected = [
                st.session_state.messages[i]
                for i in sorted(st.session_state.selected_messages)
            ]
            dialog = {
                "session_id": f"dialog_branch_{int(time.time())}",
                "source": "streamlit_ui",
                "theme_tags": [],
                "messages": selected,
            }
            dialog_json = json.dumps(dialog, ensure_ascii=False, indent=2)
            st.download_button(
                label=L["download_selected"],
                data=dialog_json,
                file_name=f"branch_{dialog['session_id']}.json",
                mime="application/json",
            )
        else:
            st.warning(L["warning_no_selection"])

with col2:
    if st.button(L["save_all"]):
        if st.session_state.messages:
            dialog = {
                "session_id": f"dialog_full_{int(time.time())}",
                "source": "streamlit_ui",
                "theme_tags": [],
                "messages": st.session_state.messages,
            }
            dialog_json = json.dumps(dialog, ensure_ascii=False, indent=2)
            st.download_button(
                label=L["download_all"],
                data=dialog_json,
                file_name=f"dialog_{dialog['session_id']}.json",
                mime="application/json",
            )
        else:
            st.warning(L["warning_no_messages"])

with col3:
    uploaded_file = st.file_uploader(
        L["load_dialog"], type="json", label_visibility="collapsed", key="load_dialog"
    )
    if uploaded_file is not None:
        try:
            dialog_data = json.load(uploaded_file)
            st.session_state.messages = dialog_data.get("messages", [])
            st.session_state.selected_messages = set()
            st.success(
                f"{L['success_load']}"
                f"{len(st.session_state.messages)}"
                f"{L['messages_loaded']}"
            )
            st.rerun()
        except Exception as e:
            st.error(f"{L['error_persona_update']} {e}")
