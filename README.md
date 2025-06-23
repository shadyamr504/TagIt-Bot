# 🔖 TagIt Bot – Telegram Link Organizer

A Telegram bot to help you save, organize, and browse your favorite links using tags. Built with Python, SQLite, and ❤️

---

## 📌 Overview

TagIt is a simple and user-friendly Telegram bot that allows users to organize their important links using custom tags. Whether you're saving study resources, articles, or tools, TagIt makes them easy to access and manage.

---

## 📚 Table of Contents

* [✨ Features](#-features)
* [⚙️ Technologies Used](#-technologies-used)
* [🧰 Installation & Setup](#-installation--setup)
* [🖥 Usage](#-usage)
* [📁 Project Structure](#-project-structure)
* [🔐 Environment Variables](#-environment-variables)
* [🤝 Contributing](#-contributing)
* [📝 License](#-license)

---

## ✨ Features

* 🏷 Add and manage custom tags
* 🔗 Save links and associate them with tags
* 📂 Browse tags and view saved links
* ✏️ Rename or ❌ delete tags
* 🗑️ Remove specific links
* 🧠 Thread-safe local SQLite database
* 🧑‍💻 Inline keyboard for interaction

---

## ⚙️ Technologies Used

* 🐍 Python 3.8+
* 💬 pyTelegramBotAPI (TeleBot)
* 🗃️ SQLite3
* 🔐 python-dotenv

---

## 🧰 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/shadyamr504/tagit-bot.git
cd tagit-bot
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
API_TOKEN=your_telegram_bot_token
```

### 5. Run the bot

```bash
python main.py
```

---

## 🖥 Usage

* `/start` – Initialize bot and user
* `Add Tags` – Button to add tags interactively
* `/add` – Add a new link and assign it to a tag
* `/show` – View all tags and links
* `/update` – Rename or delete tags, delete links
* `/done` – Finish adding tags
* `/help` – Show usage guide

Use the inline buttons to navigate easily and manage your data.

---

## 📁 Project Structure

```
├── main.py           # Main bot logic
├── config.py         # Loads .env variables
├── table.py          # Database table setup
├── requirements.txt  # Dependencies
├── .env.example      # Example env format
├── .gitignore        # Ignored files
└── README.md         # Documentation
```

---

## 🔐 Environment Variables

`.env` file should include:

```env
API_TOKEN=your_telegram_bot_token
```

Refer to `.env.example` for structure.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m "Add YourFeature"`
4. Push to branch: `git push origin feature/YourFeature`
5. Submit a pull request ✅

---

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for more information.

---

## 📄 .gitignore

```gitignore
.venv/
__pycache__/
*.py[cod]
.env
*.db
.idea/
```
