# 🎓 LearnIQ – AI-Powered Learning & Quiz Platform

LearnIQ is an AI-powered learning platform that generates personalized quizzes and viva questions using Google's Gemini API. It helps students practice, evaluate their knowledge, and receive AI-generated feedback through an interactive and responsive web application.

---

## 🚀 Live Demo

🌐 https://learniq-xpvc.onrender.com

---

## 📌 Features

- 🔐 Secure User Authentication (Login & Registration)
- 🤖 AI-Generated Quiz Questions using Google Gemini API
- 🎤 AI Viva Assessment
- 📊 Performance Dashboard
- 🏆 Leaderboard
- 📚 Assessment History
- 🌙 Dark Mode
- 📱 Fully Responsive (Desktop & Mobile)
- 📈 Learning Analytics
- 💾 SQLite Database
- ⚡ Fast Flask Backend

---

## 🛠 Tech Stack

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Jinja2 Templates

### Backend
- Python
- Flask

### Database
- SQLite

### AI
- Google Gemini API

### Deployment
- Render

### Version Control
- Git
- GitHub

---

## 📂 Project Structure

```text
LearnIQ/
│
├── static/
│   ├── style.css
│   ├── logo.png
│   └── logo_icon.png
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── quiz.html
│   ├── result.html
│   ├── history.html
│   ├── leaderboard.html
│   ├── viva.html
│   └── viva_result.html
│
├── app.py
├── database.py
├── gemini_service.py
├── requirements.txt
├── README.md
└── quiz_history.db
```

---

## ⚙ Installation

### 1. Clone the repository

```bash
git clone https://github.com/harisraveen/LearnIQ.git
```

### 2. Navigate into the project

```bash
cd LearnIQ
```

### 3. Create a virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### 6. Run the application

```bash
python app.py
```

The application will be available at

```
http://127.0.0.1:5000
```


## 🎯 Future Enhancements

- Email Verification
- Forgot Password
- PDF Report Generation
- AI Study Roadmap
- Certificates
- Admin Dashboard
- Topic Recommendations
- Notifications
- Cloud Database (PostgreSQL)
- OAuth Login (Google)

---

## 👨‍💻 Author

**Haris Raveen S S**

- GitHub: https://github.com/harisraveen

---

## 📜 License

This project is developed for educational and portfolio purposes.
