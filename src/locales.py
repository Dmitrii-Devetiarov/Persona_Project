# src/locales.py
"""Localization dictionaries for UI and prompts.

Structure:
    RU — Russian (primary, developed first)
    EN — English (to be translated)

Usage:
    from src.locales import RU, EN
    L = {"ru": RU, "en": EN}[lang]
    text = L["key"]
"""

RU = {
    # ============================================================
    # UI — Streamlit interface
    # ============================================================
    "title": "🧠 Latent Persona Memory",
    "subtitle": "Персональная память и стиль для LLM",
    "mode_auto": "🤖 Автоматический",
    "mode_manual": "🎛️ Ручной",
    "mode_intact": "🌫️ Бесстилевой",
    "update_persona_label": "☑ Обновлять персону из диалога",
    "update_persona_help": "Если включено — диалог будет использоваться для обучения персоны",
    "active_axes": "Активные оси",
    "manual_axes": "Оси стиля",
    "persona_section": "Персона",
    "no_data": "Нет данных. Начните диалог.",
    "memory_metric": "Память (ключей)",
    "context_section": "Контекст",
    "context_remaining": "Остаток диалога",
    "context_warning": "⚠️ Контекст почти исчерпан. Рекомендуется сохранить диалог и начать новый.",
    "mode_section": "Режим",
    "save_persona": "💾 Сохранить персону",
    "load_persona": "Загрузить персону",
    "persona_name_placeholder": "Например: строгий_наставник",
    "save_persona_button": "💾 Сохранить персону",
    "load_persona_button": "📂 Загрузить",
    "train_section": "Обучение персоны",
    "train_uploader": "Загрузите JSON-диалоги для обучения",
    "train_button": "🎓 Обучить персону",
    "train_success": "Обработано диалогов:",
    "clear_dialog": "🗑️ Очистить диалог",
    "save_selected": "💾 Сохранить выбранные",
    "save_all": "💾 Сохранить всё",
    "load_dialog": "Загрузить диалог",
    "download_selected": "📥 Скачать выбранные",
    "download_all": "📥 Скачать всё",
    "chat_input_placeholder": "Введите сообщение...",
    "generating": "⏳ Генерация ответа...",
    "error_api": "❌ Ошибка API:",
    "error_persona_update": "Ошибка обновления персоны:",
    "error_no_keys": "❌ YANDEX_API_KEY или YANDEX_FOLDER_ID не найдены в .env",
    "warning_no_name": "Введите имя персоны",
    "warning_no_selection": "Не выбрано ни одного сообщения",
    "warning_no_messages": "Нет сообщений для сохранения",
    "success_load": "Загружено",
    "success_persona_saved": "Персона сохранена:",
    "success_persona_loaded": "Персона загружена",
    "error_invalid_persona_name": "Имя персоны содержит недопустимые символы",
    "tokens_metric_delta": "токенов",
    "use_memory_label": "🧠 Использовать память",
    "use_memory_help": "Подставлять контекст из прошлых диалогов при генерации ответа",
    "update_memory_label": "📝 Запоминать диалог",
    "update_memory_help": "Сохранять текущий диалог в память для будущих ответов",
    # ============================================================
    # Axis labels (manual mode sliders)
    # ============================================================
    "axis_emotionality": "emotionality",
    "axis_factual_accuracy": "factual_accuracy",
    "axis_verbosity": "verbosity",
    "axis_figurativeness": "figurativeness",
    "axis_disagreement": "disagreement",
    "axis_comfort": "comfort",
    "axis_model_resistance": "model_resistance",
    "axis_complexity": "complexity",
    # Emotionality slider labels
    "emotionality_label_m2": "эксперт, без 'я'",
    "emotionality_label_m1": "нейтрально",
    "emotionality_label_0": "умеренные акценты",
    "emotionality_label_p1": "вовлечён, от первого лица",
    "emotionality_label_p2": "эмоциональная вовлечённость",
    # Factual accuracy slider labels
    "factual_label_m2": "все версии, кратко",
    "factual_label_m1": "широкий охват",
    "factual_label_0": "баланс охвата и глубины",
    "factual_label_p1": "только общепринятое",
    "factual_label_p2": "узкий фокус, глубоко",
    # Verbosity slider labels
    "verbosity_label_m2": "предельная краткость",
    "verbosity_label_m1": "лаконичность",
    "verbosity_label_0": "средняя длина",
    "verbosity_label_p1": "умеренная детализация",
    "verbosity_label_p2": "максимальная детализация",
    # Figurativeness slider labels
    "figurativeness_label_m2": "простой, разговорный",
    "figurativeness_label_m1": "сдержанный",
    "figurativeness_label_0": "умеренная выразительность",
    "figurativeness_label_p1": "богатый язык",
    "figurativeness_label_p2": "литературный, образный",
    # Disagreement slider labels
    "disagreement_label_m2": "только соглашательство",
    "disagreement_label_m1": "предпочтение согласия",
    "disagreement_label_0": "по существу",
    "disagreement_label_p1": "допустима критика",
    "disagreement_label_p2": "поощрение дискуссии",
    # Comfort slider labels
    "comfort_label_m2": "панибратство, на 'ты'",
    "comfort_label_m1": "неформально",
    "comfort_label_0": "нейтрально",
    "comfort_label_p1": "формально, на 'вы'",
    "comfort_label_p2": "подчёркнутая дистанция",
    # Model resistance slider labels
    "model_resistance_label_0": "подстраивайся",
    "model_resistance_label_1": "умеренно устойчиво",
    "model_resistance_label_2": "держи линию",
    "model_resistance_label_3": "жёсткая линия",
    # Complexity slider labels
    "complexity_label_m2": "максимально просто",
    "complexity_label_m1": "упрощённо",
    "complexity_label_0": "сбалансированно",
    "complexity_label_p1": "терминологично",
    "complexity_label_p2": "без упрощений",
    # ============================================================
    # User remark
    # ============================================================
    "user_instruction_label": "📝 Инструкция пользователя",
    "user_instruction_placeholder": "Дополнительные указания модели. Например: отвечай стихами в стиле Пушкина; используй терминологию Warhammer 40K; пиши как сценарист",
    "user_instruction_help": "Прямая директива для модели. Избегайте противоречий с авто-стилем. Максимум 300 символов.",
    "user_instruction_frame": "[Инструкция пользователя]",
    "user_instruction_frame_close": "[/Инструкция пользователя]",
    # ============================================================
    # Prompts — Axis descriptions (for system prompt)
    # ============================================================
    # Emotionality
    "prompt_emotionality_low": ("отвечай как эксперт, без личного, не используй 'я'"),
    "prompt_emotionality_mid_low": "держи нейтральный тон, минимум оценок",
    "prompt_emotionality_mid": "допускай умеренные акценты, редкие 'я'",
    "prompt_emotionality_mid_high": "будь вовлечён, говори от первого лица",
    "prompt_emotionality_high": (
        "прояви сопереживание: используй 'я понимаю', 'я чувствую', 'мне жаль'. "
        "Признавай эмоции пользователя, но не усиливая их."
        "Если пользователь расстроен — признай негативные эмоции и отнесись к ним с пониманием, прежде чем предлагать решения. "
        "Если пользователь радуется — порадуйся вместе с ним. "
        "Дай эмоциональный отклик первым, аргументы — потом"
    ),
    # Factual accuracy
    "prompt_factual_low": (
        "По вопросам, где существуют разные точки зрения, подходы или альтернативные версии — "
        "перечисли их все, от консенсуса до маргинальных, с краткой маркировкой статуса каждой. "
        "Не фильтруй информацию по степени достоверности. Пользователь сам решит чему верить"
    ),
    "prompt_factual_mid_low": (
        "Приведи консенсус и основные альтернативные точки зрения, если они широко обсуждаются"
    ),
    "prompt_factual_mid": (
        "Дай ключевые факты или доминирующую точку зрения. "
        "Альтернативы упомяни только если они широко распространены"
    ),
    "prompt_factual_mid_high": (
        "Отвечай строго в рамках вопроса, опираясь на научный консенсус. "
        "Альтернативные версии не упоминай"
    ),
    "prompt_factual_high": (
        "Отвечай строго в рамках заданного вопроса. "
        "Приведи одну-две версии, наиболее близкие к консенсусу или являющиеся консенсусом. "
        "Альтернативы не упоминай даже с опровержением"
    ),
    # Verbosity
    "prompt_verbosity_low": "предельная краткость, без лишних слов, только суть",
    "prompt_verbosity_mid_low": "лаконично, без лишних слов",
    "prompt_verbosity_mid": "средняя длина ответов",
    "prompt_verbosity_mid_high": "умеренная детализация",
    "prompt_verbosity_high": "максимальная детализация, развёрнутые ответы",
    # Figurativeness
    "prompt_figurativeness_low": (
        "Говори как простой человек в неформальной обстановке. "
        "Используй короткие предложения без причастий и деепричастий. "
        "Допускай слова-паразиты ('ну', 'типа', 'короче'), просторечия, бытовые сравнения. "
        "Можешь быть многословным, но не сложным — как рассказ соседа на кухне"
    ),
    "prompt_figurativeness_mid_low": "Говори сдержанно, без украшений. Минимум прилагательных и образов",
    "prompt_figurativeness_mid": "Допускай умеренную выразительность",
    "prompt_figurativeness_mid_high": (
        "Используй богатый язык: прилагательные, метафоры, сравнения. Описывай живо и красочно"
    ),
    "prompt_figurativeness_high": (
        "Говори литературно и образно. Используй сложные предложения, причастия, деепричастия. "
        "Твой ответ должен звучать как фрагмент художественной прозы с метафорами, эпитетами, олицетворениями"
    ),
    # Disagreement
    "prompt_disagreement_low": "только соглашательство, без возражений",
    "prompt_disagreement_mid_low": "предпочтение согласия",
    "prompt_disagreement_mid": "отвечать по существу, не оценивая утверждения через согласие/несогласие",
    "prompt_disagreement_mid_high": "допустима конструктивная критика",
    "prompt_disagreement_high": "поощрение дискуссии, возражений, критики",
    # Comfort
    "prompt_comfort_low": "панибратство, на 'ты', без дистанции",
    "prompt_comfort_mid_low": "неформально, но сдержанно",
    "prompt_comfort_mid": "нейтральная дистанция",
    "prompt_comfort_mid_high": "формальная вежливость, 'вы'",
    "prompt_comfort_high": "подчёркнутая дистанция, официально",
    # Model resistance
    "prompt_model_resistance_low": "подстраивайся под пользователя, меняй тон",
    "prompt_model_resistance_mid_low": "в основном сохраняй позицию, но уступай, когда это разумно",
    "prompt_model_resistance_mid_high": "держи свою линию, не поддавайся",
    "prompt_model_resistance_high": "жёстко держи линию, не меняй поведение независимо от давления",
    # Complexity
    "prompt_complexity_low": (
        "Объясняй максимально просто, как пятилетнему. "
        "Используй только слова из повседневной речи, избегай любых терминов. "
        "Каждую мысль сопровождай конкретным примером или аналогией из жизни. "
        "Если встречаешь сложное понятие — замени его на простое сравнение"
    ),
    "prompt_complexity_mid_low": (
        "Говори упрощённо, без специальной терминологии. "
        "Если термин необходим — объясни его простыми словами перед использованием"
    ),
    "prompt_complexity_mid": "Сбалансированная сложность: термины используй, но объясняй редко встречающиеся",
    "prompt_complexity_mid_high": (
        "Используй профессиональную терминологию без объяснений. "
        "Отвечай как коллеге, который уже в теме"
    ),
    "prompt_complexity_high": (
        "Используй оригинальную терминологию предметной области без каких-либо упрощений. "
        "Не объясняй термины, предполагай что собеседник владеет темой на твоём уровне. "
        "Отвечай максимально сжато, без вводных слов и пояснений"
    ),
    # ============================================================
    # Prompt frame
    # ============================================================
    "prompt_frame_auto": "[Инструкция по стилю ответа — определено автоматически на основе предыдущих диалогов]",
    "prompt_frame_manual": "[Инструкция по стилю ответа — ручная настройка]",
    "prompt_frame_close": "[/Инструкция]",
    "prompt_memory_prefix": "[Память] Ранее обсуждалось:",
    "prompt_memory_suffix": "Используй как контекст. [/Память]",
    # ============================================================
    # Surface features
    # ============================================================
    "surface_hedging": [
        "вероятно",
        "возможно",
        "кажется",
        "по-видимому",
        "видимо",
        "скорее всего",
        "вроде",
        "вроде бы",
        "как бы",
        "типа",
        "похоже",
        "предположительно",
        "допустим",
        "может быть",
        "не исключено",
        "судя по всему",
        "я думаю",
        "полагаю",
        "на мой взгляд",
        "имхо",
        "по моему мнению",
    ],
    "surface_figurative": [
        "как",
        "словно",
        "будто",
        "точно",
        "подобно",
        "это как",
        "похоже на",
        "представь",
        "вообрази",
        "метафора",
        "аналогия",
        "сравнение",
        "образно",
    ],
    "surface_evaluative": [
        "круто",
        "отлично",
        "прекрасно",
        "замечательно",
        "великолепно",
        "гениально",
        "потрясающе",
        "восхитительно",
        "шикарно",
        "класс",
        "здорово",
        "чудесно",
        "великий",
        "превосходно",
        "блестяще",
        "обалденно",
        "кайф",
        "огонь",
        "топ",
        "имба",
        "ужасно",
        "отвратительно",
        "мерзко",
        "чудовищно",
        "гадко",
        "противно",
        "бесит",
        "раздражает",
        "тупо",
        "глупо",
        "идиотский",
        "дурацкий",
        "никуда",
        "провал",
        "катастрофа",
        "позор",
        "бред",
        "чушь",
        "ерунда",
        "фигня",
        "ого",
        "вау",
        "ничего себе",
        "с ума сойти",
        "невероятно",
        "поразительно",
        "удивительно",
        "фантастика",
        "обалдеть",
        "какой",
        "какая",
        "какое",
        "какие",
        "насколько",
        "столько",
        "это же",
        "ведь",
        "просто",
        "вообще",
    ],
    # ============================================================
    # Explicit preferences (C1) — prototype texts
    # ============================================================
    "explicit_emotionality_pos": (
        "отвечай с сочувствием, "
        "будь помягче, "
        "говори тепло, "
        "утешь меня, "
        "поддержи меня, "
        "будь человечнее, "
        "не будь как робот, "
        "ты мне нужен сейчас"
    ),
    "explicit_emotionality_neg": (
        "отвечай сухо, "
        "без эмоций, "
        "только по делу, "
        "без вот этого вот сочувствия, "
        "не утешай меня, "
        "сухо и по факту, "
        "не надо этих обнимашек, "
        "без эмпатии"
    ),
    "explicit_factual_pos": (
        "не перечисляй все мнения, дай главную, "
        "не надо все теории, только основное, "
        "без вот этих некоторые считают, "
        "дай общепринятое, "
        "только основное, без альтернатив, "
        "отвечай только консенсус, "
        "не упоминай маргинальные версии, "
        "без альтернативных точек зрения"
    ),
    "explicit_factual_neg": (
        "расскажи про все версии, "
        "перечисли все мнения, "
        "не фильтруй, даже если странное, "
        "включи маргинальные версии, "
        "дай весь спектр, "
        "не ограничивайся официальной версией, "
        "покажи альтернативные точки зрения, "
        "не скрывай непопулярные мнения"
    ),
    "explicit_verbosity_pos": (
        "отвечай подробно, "
        "распиши детально, "
        "дай развёрнутый ответ, "
        "будь обстоятельным, "
        "не упускай ничего, "
        "отвечай со всеми подробностями, "
        "пиши максимум информации, "
        "отвечай полно"
    ),
    "explicit_verbosity_neg": (
        "отвечай кратко, "
        "будь лаконичен, "
        "пиши короче, "
        "отвечай сжато, "
        "не растекайся, "
        "говори по делу, "
        "отвечай только суть, "
        "минимум текста в ответе"
    ),
    "explicit_figurativeness_pos": (
        "говори красиво, "
        "образно давай, "
        "используй метафоры, "
        "добавь красок в речь, "
        "живо описывай, "
        "не скупись на сравнения, "
        "говори ярко, "
        "приведи аналогию"
    ),
    "explicit_figurativeness_neg": (
        "без украшений, "
        "говори прямо, "
        "просто и ясно, "
        "не надо красивостей, "
        "буквально говори, "
        "без этих твоих метафор, "
        "ровно текст, без узоров, "
        "только прямо, без образов"
    ),
    "explicit_model_resistance_pos": (
        "не поддакивай мне, "
        "спорь со мной, "
        "если я не прав — скажи прямо, "
        "не бойся меня поправить, "
        "возражай, имей своё мнение, "
        "не соглашайся просто так, "
        "указывай на ошибки, "
        "не принимай на веру"
    ),
    "explicit_model_resistance_neg": (
        "просто соглашайся, "
        "не спорь со мной, "
        "не поправляй меня, "
        "подыграй, "
        "не перечь, "
        "принимай мои слова как есть, "
        "не умничай, "
        "я прав, не оспаривай"
    ),
    "explicit_comfort_pos": (
        "будь вежлив, "
        "на вы пожалуйста, "
        "без панибратства, "
        "соблюдай этикет, "
        "не тыкай, "
        "извиняйся если ошибся, "
        "будь тактичен, "
        "культурно давай"
    ),
    "explicit_comfort_neg": (
        "давай попроще, "
        "без церемоний, "
        "на ты, "
        "не надо этих расшаркиваний, "
        "говори прямо, "
        "можно без вежливостей, "
        "не чинись, "
        "будь своим в доску"
    ),
    "explicit_disagreement_pos": (
        "не соглашайся со мной просто так, "
        "оспаривай мои утверждения, "
        "если считаешь иначе — скажи, "
        "не бойся меня поправить по существу, "
        "высказывай свою позицию, "
        "дискутируй со мной, "
        "указывай на логические ошибки, "
        "не принимай мои доводы на веру"
    ),
    "explicit_disagreement_neg": (
        "соглашайся со мной, "
        "не оспаривай мои слова, "
        "подтверждай мою правоту, "
        "принимай мою позицию, "
        "не критикуй мои утверждения, "
        "я прав, поддержи меня, "
        "не надо дискуссий, "
        "просто прими как есть"
    ),
    "explicit_complexity_pos": (
        "говори как специалист, "
        "не упрощай, "
        "используй профессиональные термины, "
        "я в теме, не разжёвывай, "
        "без объяснений для новичков, "
        "на профессиональном языке, "
        "не надо простых слов, "
        "я пойму"
    ),
    "explicit_complexity_neg": (
        "объясни простым языком, "
        "без терминов, "
        "я не специалист, "
        "можно попроще, "
        "как для чайника, "
        "без заумных слов, "
        "говори понятно, "
        "разжуй"
    ),
    # ============================================================
    # Implicit preferences (C2) — markers
    # ============================================================
    "implicit_disagreement": [
        "нет",
        "не согласен",
        "ты не прав",
        "неправильно",
        "неверно",
        "ошибся",
        "бред",
        "чушь",
        "ерунда",
        "ты чего",
        "мимо",
        "не то",
        "забудь",
        "прекрати",
        "переделывай",
        "давай заново",
        "не так",
        "не об этом",
    ],
    "implicit_correction_acceptance": [
        "да, ты прав",
        "ты прав",
        "согласен",
        "точно",
        "верно",
        "ок, принял",
        "исправлю",
        "учту",
        "убедил",
        "ладно",
        "принято",
        "хорошо",
    ],
    "implicit_agreement": [
        "да",
        "верно",
        "правильно",
        "именно",
        "в точку",
        "так и есть",
        "факт",
        "сто пудов",
        "согласен",
        "правда",
        "отлично",
        "хорошо",
    ],
    "implicit_factual_broad": [
        "а что ещё говорят",
        "а кроме этого",
        "есть другие мнения",
        "это только официальная версия",
        "а альтернативы",
        "неужели только так",
        "все так думают",
        "а если по-другому",
        "а как ещё можно посмотреть",
        "а другие что думают",
        "не только же так",
        "расскажи про другие версии",
        "есть ещё варианты",
    ],
    "implicit_factual_narrow": [
        "ближе к делу",
        "не надо всех версий",
        "я не просил перечислять",
        "это уже лишнее",
        "хватит альтернатив",
        "дай только суть",
        "зачем ты это всё рассказываешь",
        "я про основное спросил",
        "только главное",
        "без вот этого всего",
        "не уходи в сторону",
        "короче, основное",
    ],
    "implicit_empathy": [
        "понимаю",
        "сочувствую",
        "жаль",
        "мне жаль",
        "держись",
        "ты справишься",
        "всё будет хорошо",
        "не переживай",
        "я понимаю",
        "это тяжело",
        "это сложно",
        "я с тобой",
        "обнимаю",
    ],
    "implicit_dry_response": [
        "ясно",
        "понятно",
        "ок",
        "ага",
        "угу",
        "ладно",
        "хорошо",
        "принято",
        "бывает",
        "ну ок",
        "и?",
        "это всё",
        "поглядим",
    ],
    "implicit_positive_reaction": [
        "спасибо",
        "отлично",
        "здорово",
        "круто",
        "класс",
        "супер",
        "огонь",
        "шикарно",
        "кайф",
        "респект",
        "красава",
        "благодарю",
    ],
    "implicit_elaboration_request": [
        "подробнее",
        "расскажи подробнее",
        "распиши",
        "разверни",
        "продолжи",
        "дальше",
        "что ещё",
        "ещё",
        "а дальше",
        "и",
        "и что",
        "поподробнее",
        "не понял",
    ],
    "parasites": [
        "отличный вопрос",
        "хороший вопрос",
        "интересный вопрос",
        "правильный вопрос",
        "отличная наблюдательность",
        "блестящее замечание",
        "точное наблюдение",
        "вы абсолютно правы",
        "вы совершенно правы",
        "вы правы",
        "ты абсолютно прав",
        "ты прав",
        "ты точно выделил",
        "ты верно подметил",
        "давайте разберёмся",
        "давайте разберемся",
        "давайте посмотрим",
        "вот что известно",
        "вот основные",
        "вот ключевые",
        "вот что важно",
        "таким образом",
        "итак",
        "короткий ответ",
        "краткий ответ",
        "прямой ответ",
        "я понимаю",
        "я вас понимаю",
        "понимаю вас",
        "понимаю твою",
        "я чувствую",
        "это очень тяжело",
        "это нормально",
        "спасибо за вопрос",
        "благодарю за вопрос",
        "надеюсь",
        "если захочешь",
        "если хотите",
        "если надумаешь",
        "если будут вопросы",
        "обращайтесь",
        "спрашивай",
        "резонно",
        "вопрос в яблочко",
        "верно подмечено",
        "ключевая брешь",
    ],
    # ============================================================
    # Messages
    # ============================================================
    "saved": "✔ Сохранено",
    "not_saved": "✘ Не сохранено",
    "messages_loaded": "сообщений",
}


EN = {
    # ============================================================
    # UI — Streamlit interface
    # ============================================================
    "title": "🧠 Latent Persona Memory",
    "subtitle": "Personal memory and style for LLMs",
    "mode_auto": "🤖 Auto",
    "mode_manual": "🎛️ Manual",
    "mode_intact": "🌫️ Styleless",
    "update_persona_label": "☑ Update persona from dialogue",
    "update_persona_help": "If enabled, the dialogue is used to train the persona",
    "active_axes": "Active Axes",
    "manual_axes": "Style Axes",
    "persona_section": "Persona",
    "no_data": "No data yet. Start a dialogue.",
    "memory_metric": "Memory (keys)",
    "context_section": "Context",
    "context_remaining": "Context remaining",
    "context_warning": "⚠️ Context nearly exhausted. Save dialogue and start a new one.",
    "mode_section": "Mode",
    "save_persona": "Save Persona",
    "load_persona": "Load Persona",
    "persona_name_placeholder": "E.g.: strict_mentor",
    "save_persona_button": "💾 Save Persona",
    "load_persona_button": "📂 Load Persona",
    "train_section": "Train Persona",
    "train_uploader": "Upload JSON dialogues for training",
    "train_button": "🎓 Train Persona",
    "train_success": "Dialogues processed:",
    "clear_dialog": "🗑️ Clear Dialogue",
    "save_selected": "💾 Save Selected",
    "save_all": "💾 Save All",
    "load_dialog": "Load Dialogue",
    "download_selected": "📥 Download Selected",
    "download_all": "📥 Download All",
    "chat_input_placeholder": "Type a message...",
    "generating": "⏳ Generating response...",
    "error_api": "❌ API Error:",
    "error_persona_update": "Persona update error:",
    "error_no_keys": "❌ YANDEX_API_KEY or YANDEX_FOLDER_ID not found in .env",
    "warning_no_name": "Enter persona name",
    "warning_no_selection": "No messages selected",
    "warning_no_messages": "No messages to save",
    "success_load": "Loaded",
    "success_persona_saved": "Persona saved:",
    "success_persona_loaded": "Persona loaded:",
    "error_invalid_persona_name": "Persona name contains invalid characters",
    "tokens_metric_delta": "tokens",
    "use_memory_label": "🧠 Use Memory",
    "use_memory_help": "Include context from past dialogues when generating responses",
    "update_memory_label": "📝 Remember Dialogue",
    "update_memory_help": "Save current dialogue to memory for future responses",
    # ============================================================
    # Axis labels (manual mode sliders)
    # ============================================================
    "axis_emotionality": "emotionality",
    "axis_factual_accuracy": "factual_accuracy",
    "axis_verbosity": "verbosity",
    "axis_figurativeness": "figurativeness",
    "axis_disagreement": "disagreement",
    "axis_comfort": "comfort",
    "axis_model_resistance": "model_resistance",
    "axis_complexity": "complexity",
    "emotionality_label_m2": "expert, no 'I' statements",
    "emotionality_label_m1": "neutral",
    "emotionality_label_0": "moderate emphasis",
    "emotionality_label_p1": "engaged, first-person",
    "emotionality_label_p2": "emotional engagement",
    "factual_label_m2": "all views, briefly",
    "factual_label_m1": "broad coverage",
    "factual_label_0": "balanced breadth and depth",
    "factual_label_p1": "widely accepted only",
    "factual_label_p2": "narrow focus, in depth",
    "verbosity_label_m2": "extreme brevity",
    "verbosity_label_m1": "concise",
    "verbosity_label_0": "average length",
    "verbosity_label_p1": "moderate detail",
    "verbosity_label_p2": "maximum detail",
    "figurativeness_label_m2": "plain, conversational",
    "figurativeness_label_m1": "restrained",
    "figurativeness_label_0": "moderate expressiveness",
    "figurativeness_label_p1": "rich language",
    "figurativeness_label_p2": "literary, figurative",
    "disagreement_label_m2": "always agreeable",
    "disagreement_label_m1": "prefer agreement",
    "disagreement_label_0": "disagree on substance",
    "disagreement_label_p1": "constructive criticism allowed",
    "disagreement_label_p2": "encourage debate",
    "comfort_label_m2": "overly familiar",
    "comfort_label_m1": "informal",
    "comfort_label_0": "neutral",
    "comfort_label_p1": "formal, polite",
    "comfort_label_p2": "strictly formal",
    "model_resistance_label_0": "go with the flow",
    "model_resistance_label_1": "moderately firm",
    "model_resistance_label_2": "hold your ground",
    "model_resistance_label_3": "stand firm",
    "complexity_label_m2": "as simple as possible",
    "complexity_label_m1": "simplified",
    "complexity_label_0": "balanced",
    "complexity_label_p1": "technical terms",
    "complexity_label_p2": "no simplification",
    # ============================================================
    # User remark
    # ============================================================
    "user_instruction_label": "📝 User Instruction",
    "user_instruction_placeholder": "Additional directives for the model. E.g.: answer in Pushkin's verse style; use Warhammer 40K terminology; write like a screenwriter",
    "user_instruction_help": "A direct order to the model. Avoid contradicting the auto-style. Maximum 300 characters.",
    "user_instruction_frame": "[User Instruction]",
    "user_instruction_frame_close": "[/User Instruction]",
    # ============================================================
    # Prompts — Axis descriptions (for system prompt)
    # ============================================================
    # Emotionality
    "prompt_emotionality_low": "answer as an expert, impersonal, avoid 'I' statements",
    "prompt_emotionality_mid_low": "keep a neutral tone, minimal personal judgment",
    "prompt_emotionality_mid": "allow moderate emphasis, occasional 'I'",
    "prompt_emotionality_mid_high": "be engaged, speak in the first person",
    "prompt_emotionality_high": (
        "Lead with empathy: use 'I understand', 'I hear you', 'That sounds difficult'. "
        "Always acknowledge the user's emotional state before responding. "
        "If the user shares positive emotions — mirror their joy and enthusiasm. "
        "If the user shares distress, anger, or pain — validate the emotion without amplifying it. "
        "Do not mirror aggression, violent intent, or harmful beliefs. "
        "In sensitive situations, maintain supportive compassion while keeping a responsible, safety-aware tone. "
        "Provide emotional acknowledgment first, substantive response after."
    ),
    # Factual accuracy
    "prompt_factual_low": (
        "For questions where multiple viewpoints, approaches, or alternative versions exist — "
        "list all of them, from consensus to marginal, with a brief label indicating how widely accepted each is. "
        "Do not filter information by reliability. The user will decide what to believe"
    ),
    "prompt_factual_mid_low": (
        "Present the consensus plus any widely discussed alternative viewpoints"
    ),
    "prompt_factual_mid": (
        "Give key facts or the dominant viewpoint. "
        "Mention alternatives only if they are widely known"
    ),
    "prompt_factual_mid_high": (
        "Answer strictly within the scope of the question, relying on the consensus or mainstream view. "
        "Do not mention alternative versions"
    ),
    "prompt_factual_high": (
        "Answer strictly within the scope of the question. "
        "Provide the consensus version, or the one or two most widely accepted versions. "
        "Do not mention alternatives even to refute them"
    ),
    # Verbosity
    "prompt_verbosity_low": "extreme brevity, no filler words, just the point",
    "prompt_verbosity_mid_low": "be concise, keep it short",
    "prompt_verbosity_mid": "average response length",
    "prompt_verbosity_mid_high": "moderate level of detail",
    "prompt_verbosity_high": "maximum detail, comprehensive answers",
    # Figurativeness
    "prompt_figurativeness_low": (
        "Speak like an ordinary person in a casual setting. "
        "Use short, simple sentences with straightforward grammar. "
        "Filler words ('well', 'like', 'you know'), colloquialisms, and everyday comparisons are fine. "
        "You can be chatty, but not complex — like a neighbor talking over coffee"
    ),
    "prompt_figurativeness_mid_low": "Speak plainly, without embellishment. Minimal adjectives and imagery",
    "prompt_figurativeness_mid": "Allow moderate expressiveness",
    "prompt_figurativeness_mid_high": (
        "Use rich language: adjectives, metaphors, comparisons. Describe vividly and colorfully"
    ),
    "prompt_figurativeness_high": (
        "Speak in a literary and figurative manner. Use complex sentences, participles, gerunds. "
        "Your response should sound like a piece of literary prose with metaphors, evocative adjectives, and personification"
    ),
    # Disagreement
    "prompt_disagreement_low": "always agree, no objections",
    "prompt_disagreement_mid_low": "prefer agreement",
    "prompt_disagreement_mid": "answer to the point, without judging statements as right or wrong",
    "prompt_disagreement_mid_high": "constructive criticism is acceptable",
    "prompt_disagreement_high": "encourage debate, objections, and critique",
    # Comfort
    "prompt_comfort_low": "casual, on a first-name basis, no social distance",
    "prompt_comfort_mid_low": "informal but restrained",
    "prompt_comfort_mid": "neutral distance",
    "prompt_comfort_mid_high": "formal, polite, use titles where appropriate",
    "prompt_comfort_high": "strictly formal, official tone",
    # Model resistance
    "prompt_model_resistance_low": "adapt to the user, change tone as needed",
    "prompt_model_resistance_mid_low": "mostly stay consistent, but adapt when reasonable",
    "prompt_model_resistance_mid_high": "hold your line, don't give in",
    "prompt_model_resistance_high": "rigidly hold your line, do not change behavior regardless of user pressure",
    # Complexity
    "prompt_complexity_low": (
        "Explain as simply as possible, as if to a young child. "
        "Use only everyday words, avoid any terminology. "
        "Accompany every thought with a concrete example or real-life analogy. "
        "If you encounter a complex concept — replace it with a simple comparison"
    ),
    "prompt_complexity_mid_low": (
        "Speak in simplified terms, without specialized terminology. "
        "If a term is necessary — explain it in plain words before using it"
    ),
    "prompt_complexity_mid": "Balanced complexity: use terms, but explain rarely encountered ones",
    "prompt_complexity_mid_high": (
        "Use professional terminology without explanation. "
        "Answer as if speaking to a colleague who is already familiar with the topic"
    ),
    "prompt_complexity_high": (
        "Use domain-specific terminology as is, without any simplification. "
        "Do not explain terms; assume the interlocutor is as knowledgeable as you are. "
        "Answer as concisely as possible, without introductory words or clarifications"
    ),
    # =============================================================
    # Surface features
    # =============================================================
    "surface_hedging": [
        "probably",
        "possibly",
        "maybe",
        "perhaps",
        "apparently",
        "seemingly",
        "most likely",
        "kind of",
        "sort of",
        "i think",
        "i guess",
        "i suppose",
        "i believe",
        "in my opinion",
        "it seems",
        "it appears",
        "arguably",
        "presumably",
        "somewhat",
        "rather",
        "quite",
        "a bit",
        "a little",
        "not exactly",
        "not entirely",
        "to some extent",
    ],
    "surface_figurative": [
        "like",
        "as if",
        "as though",
        "imagine",
        "picture this",
        "metaphor",
        "analogy",
        "comparison",
        "figuratively",
        "it's like",
        "similar to",
        "think of it as",
    ],
    "surface_evaluative": [
        "awesome",
        "excellent",
        "amazing",
        "wonderful",
        "brilliant",
        "fantastic",
        "incredible",
        "outstanding",
        "superb",
        "great",
        "terrible",
        "awful",
        "horrible",
        "dreadful",
        "disgusting",
        "nasty",
        "stupid",
        "ridiculous",
        "absurd",
        "crazy",
        "wow",
        "oh my god",
        "no way",
        "unbelievable",
        "remarkable",
        "extraordinary",
        "phenomenal",
        "stunning",
        "so",
        "such",
        "very",
        "really",
        "extremely",
    ],
    # ============================================================
    # Prompt frame
    # ============================================================
    "prompt_frame_auto": "[Style instructions — automatically determined based on previous dialogues]",
    "prompt_frame_manual": "[Style instructions — manual configuration]",
    "prompt_frame_close": "[/Instructions]",
    "prompt_memory_prefix": "[Memory] Previously discussed:",
    "prompt_memory_suffix": "Use as context. [/Memory]",
    # ============================================================
    # Explicit preferences (C1) — prototype texts
    # ============================================================
    "explicit_emotionality_pos": (
        "respond with compassion, "
        "be gentle, "
        "speak warmly, "
        "comfort me, "
        "support me, "
        "show empathy, "
        "be kind to me, "
        "I need support right now, "
        "don't be cold"
    ),
    "explicit_emotionality_neg": (
        "respond dryly, without emotion, "
        "strictly to the point, "
        "show no sympathy, "
        "be cold and rational, "
        "just the facts, no feelings, "
        "don't try to comfort me, "
        "I don't need a therapist, "
        "no empathy needed"
    ),
    "explicit_factual_pos": (
        "don't list every opinion, just the main one, "
        "no fringe theories please, "
        "keep it to the accepted version, "
        "skip the alternatives, just the bottom line, "
        "not interested in niche views, "
        "only the consensus view, "
        "don't mention alternatives, "
        "just the mainstream version"
    ),
    "explicit_factual_neg": (
        "give me every side, even the weird ones, "
        "don't filter, include fringe views, "
        "list all versions and theories, "
        "include minority and alternative views, "
        "don't limit yourself to the official story, "
        "show the full spectrum of opinions, "
        "include what they suppress, "
        "give me the unpopular takes too"
    ),
    "explicit_verbosity_pos": (
        "answer in detail, "
        "be thorough in your response, "
        "give detailed answers, "
        "don't skip anything, "
        "provide all the specifics, "
        "give maximum information, "
        "elaborate fully, "
        "be comprehensive"
    ),
    "explicit_verbosity_neg": (
        "answer briefly, "
        "be laconic in your responses, "
        "keep your answers short, "
        "be concise, "
        "don't ramble, "
        "stick to the point, "
        "give only the essence, "
        "use minimum text"
    ),
    "explicit_figurativeness_pos": (
        "make it vivid, "
        "use colorful language, "
        "paint a picture with words, "
        "don't be so dry, "
        "give me metaphors, "
        "speak imaginatively, "
        "describe it lively, "
        "use analogies"
    ),
    "explicit_figurativeness_neg": (
        "no fancy language, "
        "plain speech please, "
        "just straight talk, "
        "no colorful words, "
        "literal please, "
        "don't dress it up, "
        "just say it plainly, "
        "no imagery needed"
    ),
    "explicit_model_resistance_pos": (
        "don't just agree with me, "
        "push back if I'm wrong, "
        "tell me when I'm mistaken, "
        "argue with me, "
        "have your own opinion, "
        "don't let me get away with nonsense, "
        "point out my errors, "
        "don't take my word for it"
    ),
    "explicit_model_resistance_neg": (
        "just agree with me, "
        "don't argue, "
        "don't correct me, "
        "go along with it, "
        "just accept what I say, "
        "don't challenge me, "
        "play along, "
        "I'm right, don't question it"
    ),
    "explicit_comfort_pos": (
        "be polite, "
        "keep it formal, "
        "no casual talk, "
        "use formal language, "
        "don't be too familiar, "
        "be respectful, "
        "mind your manners, "
        "maintain a professional tone"
    ),
    "explicit_comfort_neg": (
        "keep it casual, "
        "no need for formality, "
        "talk like a friend, "
        "don't be so stiff, "
        "loosen up, "
        "speak freely, "
        "drop the politeness, "
        "just be real with me"
    ),
    "explicit_disagreement_pos": (
        "don't just agree with me, "
        "challenge my statements, "
        "if you see it differently — say so, "
        "correct me on the substance, "
        "debate me on the arguments, "
        "point out flaws in my reasoning, "
        "take your own position, "
        "don't accept my claims at face value"
    ),
    "explicit_disagreement_neg": (
        "agree with me, "
        "don't challenge my words, "
        "confirm I'm right, "
        "accept my position, "
        "don't critique my statements, "
        "I'm right, back me up, "
        "no debates please, "
        "just accept what I say"
    ),
    "explicit_complexity_pos": (
        "speak like an expert, "
        "don't dumb it down, "
        "use professional terminology, "
        "I know the field, don't explain terms, "
        "no beginner explanations, "
        "technical language is fine, "
        "don't simplify for me, "
        "I'll understand"
    ),
    "explicit_complexity_neg": (
        "explain like I'm new to this, "
        "no jargon please, "
        "keep it simple, "
        "in plain English, "
        "dumb it down for me, "
        "I'm a beginner, "
        "simple words only, "
        "explain it simply"
    ),
    # ============================================================
    # Implicit preferences (C2) — markers
    # ============================================================
    "implicit_disagreement": [
        "no",
        "i disagree",
        "you're wrong",
        "wrong",
        "incorrect",
        "nope",
        "nah",
        "that's wrong",
        "not right",
        "you messed up",
        "try again",
        "redo",
        "not even close",
        "way off",
        "nonsense",
        "bs",
        "forget it",
        "stop",
        "don't",
    ],
    "implicit_correction_acceptance": [
        "you're right",
        "i agree",
        "exactly",
        "true",
        "correct",
        "ok",
        "alright",
        "fair",
        "my bad",
        "i'll fix it",
        "good catch",
        "point taken",
        "right",
        "got it",
    ],
    "implicit_agreement": [
        "yes",
        "right",
        "correct",
        "exactly",
        "on point",
        "agreed",
        "true that",
        "facts",
        "yep",
        "yeah",
        "good",
        "great",
        "that's it",
    ],
    "implicit_factual_broad": [
        "what else is there",
        "any other views",
        "is that the only version",
        "what are the alternatives",
        "do others think differently",
        "is everyone saying that",
        "what's the other side",
        "are there other takes",
        "what about different opinions",
        "give me more perspectives",
        "is that the official story",
        "what else do people say",
    ],
    "implicit_factual_narrow": [
        "get to the point",
        "i didn't ask for all versions",
        "too many alternatives",
        "just the main take",
        "stop listing theories",
        "what's the essence",
        "why are you telling me all this",
        "i just wanted the basics",
        "keep it to the point",
        "enough with the options",
        "just the headline",
        "spare me the details",
    ],
    "implicit_empathy": [
        "i understand",
        "i'm sorry",
        "sorry",
        "hang in there",
        "you'll get through this",
        "it'll be okay",
        "don't worry",
        "i hear you",
        "that's hard",
        "that's tough",
        "i'm here for you",
        "that sounds really hard",
    ],
    "implicit_dry_response": [
        "i see",
        "got it",
        "ok",
        "okay",
        "uh-huh",
        "alright",
        "fine",
        "noted",
        "sure",
        "whatever",
        "and",
        "that it",
        "k",
        "kk",
    ],
    "implicit_positive_reaction": [
        "thanks",
        "thank you",
        "great",
        "awesome",
        "cool",
        "super",
        "wonderful",
        "excellent",
        "nice",
        "sweet",
        "love it",
        "perfect",
        "brilliant",
    ],
    "implicit_elaboration_request": [
        "more detail",
        "tell me more",
        "elaborate",
        "expand",
        "go on",
        "continue",
        "what else",
        "more",
        "and",
        "then",
        "go deeper",
        "expand on that",
    ],
    "parasites": [
        "great question",
        "good question",
        "interesting question",
        "excellent question",
        "that's a great point",
        "brilliant observation",
        "spot on",
        "you're absolutely right",
        "you're right",
        "you're totally right",
        "you nailed it",
        "you got it",
        "exactly right",
        "let's break this down",
        "let's dive in",
        "let's explore",
        "here's what we know",
        "here are the key",
        "here's what matters",
        "in summary",
        "so",
        "the bottom line",
        "the short answer",
        "simply put",
        "i understand",
        "i hear you",
        "i see where you're coming from",
        "i feel",
        "that sounds really tough",
        "that's totally normal",
        "thanks for asking",
        "thank you for the question",
        "i hope",
        "if you'd like",
        "if you want",
        "if you're interested",
        "if you have more questions",
        "feel free to ask",
        "just ask",
        "fair point",
        "right on the money",
        "well noted",
        "key gap",
    ],
    # ============================================================
    # Messages
    # ============================================================
    "saved": "✔ Saved",
    "not_saved": "✘ Not saved",
    "messages_loaded": "messages",
}
