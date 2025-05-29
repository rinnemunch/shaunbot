import sys
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QFileDialog



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
        self.worker = None
        self.conversation = [
            {"role": "system", "content": "You are Shaunbot, a helpful and chill AI assistant."}
        ]

        self.setWindowTitle("Shaunbot 🤖")
        self.setGeometry(200, 200, 500, 600)

        self.layout = QVBoxLayout()

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Ask Shaunbot something...")
        self.input_line.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)

        self.layout.addWidget(self.chat_area)
        self.layout.addWidget(self.input_line)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)
        self.layout.addWidget(self.clear_button)

        self.knowledge_data = ""

        self.load_button = QPushButton("Load Knowledge File")
        self.load_button.clicked.connect(self.load_knowledge_file)
        self.layout.addWidget(self.load_button)

    def send_message(self):
        user_input = self.input_line.text().strip()
        if not user_input:
            return

        self.chat_area.append(f"🧑 You: {user_input}")
        self.input_line.clear()

        # Inject file knowledge if it exists
        if self.knowledge_data:
            system_prompt = (
                    "You are Shaunbot, a helpful and chill AI assistant. Use the following knowledge to help answer questions:\n\n"
                    + self.knowledge_data
            )
        else:
            system_prompt = "You are Shaunbot, a helpful and chill AI assistant."

        # Reset base system prompt before each run
        self.conversation[0] = {"role": "system", "content": system_prompt}
        self.conversation.append({"role": "user", "content": user_input})

        self.worker = OllamaWorker(self.conversation.copy())
        self.worker.result_ready.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, reply):
        self.current_reply = reply
        self.typing_index = 0
        self.chat_area.append("🤖 Shaunbot: ")
        self.timer = QTimer()
        self.timer.timeout.connect(self.type_next_character)
        self.timer.start(20)  # Adjustable typing speed for the bot
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
                    self.knowledge_data = file.read()
                self.chat_area.append(f"📚 Knowledge file loaded: {file_path.split('/')[-1]}")
            except Exception as e:
                self.chat_area.append(f"❌ Failed to load file: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShaunBot()
    window.show()
    sys.exit(app.exec_())
