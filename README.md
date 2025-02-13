# ❤️‍🔥 Anonymous Valentines Telegram Bot ❤️‍🔥

A simple Telegram bot for sending anonymous valentines to other users. Built with Python, SQLite, and `python-telegram-bot`

## 🚀 Features
- Send anonymous valentines to Telegram users.
- View received valentines.
- Simple database storage with SQLite.
- Easy deployment with Docker.

---

## 📦 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/besthedgehog/valentine_bot.git
cd anonymous-valentine-bot
```

### 2️⃣ Install dependencies and run (without Docker)
Ensure you have Python 3.11+ installed.

```bash
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
pip3 install -r requirements.txt
```

Create a `.env` file and set your bot token:
```bash
echo "BOT_TOKEN=your_telegram_bot_token" > .env
```

Run the bot:
```bash
python3 valentine_bot.py
```

---

## 🐳 Run with Docker

### 1️⃣ Build and start the container
```bash
docker-compose up --build -d
```

### 2️⃣ Stop the bot
```bash
docker-compose down
```

---

## 🛠️ Configuration
The bot requires a `.env` file with the following:
```
BOT_TOKEN=your_telegram_bot_token
```

The database (`valentines.db`) is automatically created in the project root.

---

## 📜 License
This project is licensed under the MIT License.

---

## 🤝 Contributing
Feel free to submit issues and pull requests!

---

## 📬 Contact
For any questions open an issue on GitHub.

---

## ❤️‍🔥 Happy Valentine's Day! ❤️‍🔥

