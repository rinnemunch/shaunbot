from PyQt5.QtWidgets import QPushButton, QComboBox


def create_sidebar_buttons(bot):
    # Buttons
    save_btn = QPushButton("Save Chat")
    save_btn.clicked.connect(bot.save_chat)

    load_chat_btn = QPushButton("Load Chat")
    load_chat_btn.clicked.connect(bot.load_chat)

    load_knowledge_btn = QPushButton("Load Knowledge File")
    load_knowledge_btn.clicked.connect(bot.load_knowledge_file)

    clear_btn = QPushButton("Clear Chat")
    clear_btn.clicked.connect(bot.clear_chat)

    history_btn = QPushButton("View History")
    history_btn.clicked.connect(bot.show_history)

    theme_btn = QPushButton("Toggle Theme")
    theme_btn.clicked.connect(bot.toggle_theme)

    # ComboBoxes
    mode_selector = QComboBox()
    mode_selector.addItems([
        "Chill Mode 😎", "Tech Support 🛠️", "Motivator 💪", "Dad Joke Bot 👴"
    ])

    model_selector = QComboBox()
    model_selector.addItems(["llama3", "mistral", "llama2"])

    return {
        "save": save_btn,
        "load_chat": load_chat_btn,
        "load_knowledge": load_knowledge_btn,
        "clear": clear_btn,
        "history": history_btn,
        "theme": theme_btn,
        "mode": mode_selector,
        "model": model_selector
    }
