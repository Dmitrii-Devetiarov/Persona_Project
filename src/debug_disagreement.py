# scripts/debug_disagreement.py
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.persona_manager import PersonaManager
from src.implicit_preferences import ImplicitPreferenceTracker
from src.style_surface import SurfaceStyleTracker
import json

# Проверяем только C2 на втором диалоге
test_file = PROJECT_ROOT / "data" / "user_dialogs" / "dialog_2.json"
with open(test_file, "r", encoding="utf-8") as f:
    dialog_data = json.load(f)

messages = dialog_data["messages"]

tracker = ImplicitPreferenceTracker(alpha=0.3)
print("C2 signals from dialog_2:")
for i in range(len(messages) - 1):
    if messages[i]["role"] == "assistant" and messages[i + 1]["role"] == "user":
        signals = tracker.analyze_reaction(messages[i]["content"], messages[i + 1]["content"])
        has_signal = any(v != 0.0 for v in signals.values())
        if has_signal:
            print(f"  User: {messages[i + 1]['content'][:80]}...")
            for k, v in signals.items():
                if v != 0.0:
                    print(f"    {k}: {v:+.2f}")
        tracker.update_inferred_preferences(signals)

final_c2 = tracker.get_inferred_vector()
print(f"\nC2 final: { {k: round(v, 3) for k, v in final_c2.items()} }")

# Проверяем surface mapping
print("\nSurface mapping from dialog_1 + dialog_2:")
manager = PersonaManager(persist=False)
for file in sorted((PROJECT_ROOT / "data" / "user_dialogs").glob("dialog_*.json")):
    with open(file, "r", encoding="utf-8") as f:
        d = json.load(f)
    user_msgs = [m["content"] for m in d["messages"] if m["role"] == "user"]
    ema = manager.style_tracker.extract_surface_features(user_msgs)
    manager.style_tracker.update_ema(ema)

b_scaled = manager._scale_surface_to_preferences(manager.style_tracker.get_ema())
print(f"B scaled: { {k: round(v, 3) for k, v in b_scaled.items()} }")