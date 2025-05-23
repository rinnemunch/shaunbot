import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
import json


class ShaunBot(QWidget):
    def __init__(self):
        super().__init__()
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

        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3",
                    "messages": [
                        {"role": "user", "content": user_input}
                    ],
                    "stream": True
                },
                stream=True  # <-- this is key
            )

            full_reply = ""
            for line in response.iter_lines():
                if line:
                    chunk = line.decode("utf-8")
                    if chunk.startswith("{"):
                        data = json.loads(chunk)
                        full_reply += data.get("message", {}).get("content", "")

            self.chat_area.append(f"🤖 Shaunbot: {full_reply.strip()}\n")

        except Exception as e:
            self.chat_area.append(f"❌ Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShaunBot()
    window.show()
    sys.exit(app.exec_())
