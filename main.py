import sys
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap



class OllamaWorker(QThread):
    result_ready = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, conversation):
        super().__init__()
        self.conversation = conversation

    def run(self):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3",
                    "messages": self.conversation,
                    "stream": True
                },
                stream=True
            )

            full_reply = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    full_reply += data.get("message", {}).get("content", "")
            self.result_ready.emit(full_reply.strip())

        except Exception as e:
            self.error.emit(str(e))


class ShaunBot(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = None
        self.typing_index = None
        self.current_reply = None
        self.worker = None
        self.knowledge_data = ""
        self.conversation = [
            {"role": "system", "content": "You are Shaunbot, a helpful and chill AI assistant."}
        ]

        self.setWindowTitle("Shaunbot 🤖")
        self.setGeometry(200, 200, 800, 600)

        # Layouts
        self.main_layout = QHBoxLayout()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(8)
        self.chat_layout = QVBoxLayout()

        self.character_layout = QVBoxLayout()
        self.character_label = QLabel()
        self.character_label.setFixedSize(150, 150)  # adjustable for logo image
        self.character_label.setStyleSheet("border: 2px solid black; border-radius: 10px;")
        self.character_label.setAlignment(Qt.AlignCenter)
        self.character_layout.addWidget(self.character_label)

        self.character_label.setPixmap(QPixmap("shaun.png").scaled(
            self.character_label.width(),
            self.character_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

        # --- Sidebar Widgets ---
        self.save_button = QPushButton("Save Chat")
        self.save_button.clicked.connect(self.save_chat)

        self.load_chat_button = QPushButton("Load Chat")
        self.load_chat_button.clicked.connect(self.load_chat)

        self.load_button = QPushButton("Load Knowledge File")
        self.load_button.clicked.connect(self.load_knowledge_file)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "Chill Mode 😎",
            "Tech Support 🛠️",
            "Motivator 💪",
            "Dad Joke Bot 👴"
        ])

        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama3", "mistral", "llama2"])

        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)

        title_label = QLabel("Shaunbot")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")

        self.sidebar_layout.addWidget(title_label)
        self.sidebar_layout.addWidget(self.save_button)
        self.sidebar_layout.addWidget(self.load_chat_button)
        self.sidebar_layout.addWidget(self.load_button)
        self.sidebar_layout.addWidget(self.mode_selector)
        self.sidebar_layout.addWidget(self.model_selector)
        self.sidebar_layout.addWidget(self.clear_button)

        self.sidebar_layout.addStretch()  # This pushes everything above to the top

        # --- Chat Area ---
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Ask Shaunbot something...")
        self.input_line.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.chat_layout.addWidget(self.chat_area)
        self.chat_layout.addWidget(self.input_line)

        send_row = QHBoxLayout()
        send_row.addWidget(self.send_button)
        self.chat_layout.addLayout(send_row)

        # --- Final Layout Assembly ---

        chat_wrapper = QHBoxLayout()
        chat_wrapper.addLayout(self.chat_layout, 4)

        character_wrapper = QVBoxLayout()
        character_wrapper.addLayout(self.character_layout)
        character_wrapper.addStretch()
        chat_wrapper.addLayout(character_wrapper, 2)

        self.main_layout.addLayout(self.sidebar_layout, 1)
        self.main_layout.addLayout(chat_wrapper, 5)

        self.setLayout(self.main_layout)

    def send_message(self):
        user_input = self.input_line.text().strip()
        if not user_input:
            return

        self.chat_area.append(f"🧑 You: {user_input}")
        self.input_line.clear()
        self.chat_area.append("<i>🤖 Shaunbot is typing...</i>")

        mode = self.mode_selector.currentText()

        if mode == "Chill Mode 😎":
            base_prompt = "You are Shaunbot, a helpful and chill AI assistant."
        elif mode == "Tech Support 🛠️":
            base_prompt = "You are Shaunbot, a focused tech support assistant. Answer questions in a concise, technical way."
        elif mode == "Motivator 💪":
            base_prompt = "You are Shaunbot, a motivational coach who always encourages the user with high energy."
        elif mode == "Dad Joke Bot 👴":
            base_prompt = "You are Shaunbot, a corny dad joke machine who always includes a pun in your answers."
        else:
            base_prompt = "You are Shaunbot, a helpful and chill AI assistant."

        # Add knowledge if present (Ive only tested txt files)
        if self.knowledge_data:
            system_prompt = f"{base_prompt}\n\nUse the following knowledge:\n{self.knowledge_data}"
        else:
            system_prompt = base_prompt

        # Reset base system prompt before each run
        self.conversation[0] = {"role": "system", "content": system_prompt}
        self.conversation.append({"role": "user", "content": user_input})

        self.worker = OllamaWorker(self.conversation.copy())
        self.worker.result_ready.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, reply):

        cursor = self.chat_area.textCursor()
        cursor.movePosition(cursor.End)
        cursor.select(cursor.BlockUnderCursor)
        if "<i>🤖 Shaunbot is typing...</i>" in cursor.selectedText():
            cursor.removeSelectedText()
            cursor.deletePreviousChar()

        if not reply.strip():
            self.chat_area.append("🤖 Shaunbot had nothing to say.")
            return

        self.current_reply = reply
        self.typing_index = 0
        self.chat_area.append("🤖 Shaunbot: ")
        self.timer = QTimer()
        self.timer.timeout.connect(self.type_next_character)
        self.timer.start(20)
        self.conversation.append({"role": "assistant", "content": reply})

    def type_next_character(self):
        if self.typing_index < len(self.current_reply):
            self.chat_area.moveCursor(self.chat_area.textCursor().End)
            self.chat_area.insertPlainText(self.current_reply[self.typing_index])
            self.typing_index += 1
        else:
            self.timer.stop()
            self.chat_area.append("")  # Adds spacing after full reply

    def handle_error(self, error_msg):
        self.chat_area.append(f"❌ Error: {error_msg}")

    def clear_chat(self):
        self.chat_area.clear()
        self.conversation = [
            {"role": "system", "content": "You are Shaunbot, a helpful and chill AI assistant."}
        ]

    def load_knowledge_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt *.md)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    raw_text = file.read()
                    max_chars = 3000
                    self.knowledge_data = raw_text[:max_chars]
                file_name = file_path.split("/")[-1]
                char_count = len(self.knowledge_data)
                self.chat_area.append(f"📚 Loaded: {file_name} (trimmed to {char_count} characters)")
            except Exception as e:
                self.chat_area.append(f"❌ Failed to load file: {e}")

    def save_chat(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chat", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.conversation, f, indent=2)
                self.chat_area.append(f"💾 Chat saved to: {file_path.split('/')[-1]}")
            except Exception as e:
                self.chat_area.append(f"❌ Failed to save chat: {e}")

    def load_chat(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Chat", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.conversation = json.load(f)

                self.chat_area.clear()
                for msg in self.conversation:
                    role = msg["role"]
                    content = msg["content"]
                    if role == "user":
                        self.chat_area.append(f"🧑 You: {content}")
                    elif role == "assistant":
                        self.chat_area.append(f"🤖 Shaunbot: {content}")
                self.chat_area.append(f"📂 Chat loaded from: {file_path.split('/')[-1]}")
            except Exception as e:
                self.chat_area.append(f"❌ Failed to load chat: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShaunBot()
    window.show()
    sys.exit(app.exec_())
