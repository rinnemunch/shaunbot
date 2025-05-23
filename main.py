import sys
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal


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

        self.layout.addWidget(self.chat_area)
        self.layout.addWidget(self.input_line)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)


    def send_message(self):
        user_input = self.input_line.text().strip()
        if not user_input:
            return

        self.chat_area.append(f"🧑 You: {user_input}")
        self.input_line.clear()

        self.conversation.append({"role": "user", "content": user_input})
        self.worker = OllamaWorker(self.conversation.copy())
        self.worker.result_ready.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, reply):
        self.chat_area.append(f"🤖 Shaunbot: {reply}\n")
        self.conversation.append({"role": "assistant", "content": reply})

    def handle_error(self, error_msg):
        self.chat_area.append(f"❌ Error: {error_msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShaunBot()
    window.show()
    sys.exit(app.exec_())
