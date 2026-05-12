# 🛡️ AI Fake Internship & Job Detector

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Data-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An advanced web application to detect fake job and internship listings using a specialized AI scoring engine. This tool analyzes job descriptions to identify over 35+ scam indicators, including payment demands, unrealistic salaries, suspicious contact methods, and data abuse patterns, keeping applicants safe from fraudulent recruiters.

---

## 📸 Site Preview

### 🔍 Smart Analyzer
![Dashboard](docs/screenshots/dashboard.png)
*Paste any description and get an instant scam score.*

### 📊 Detailed Findings
![Analysis Result](docs/screenshots/analysis_result.png)
*See exactly why a listing was flagged with categorized red flags.*

### 📋 Analysis History
![History](docs/screenshots/history.png)
*Keep track of all your past checks in a secure archive.*

---

## ✨ Features

- **🚀 Instant Analysis**: Get a scam probability score (0–100) and risk level (Safe, Medium Risk, High Risk) in seconds.
- **🚩 Red Flag Detection**: Highlights specific suspicious phrases, vague descriptions, and high-pressure tactics.
- **🔐 Secure Authentication**: Private user accounts powered by `bcrypt` password hashing.
- **📜 Session History**: Save, manage, and review your previous analysis results.
- **🌑 Modern UI**: Sleek dark-mode interface designed for focus and readability.
- **💾 Zero-Setup Database**: Integrated SQLite database means no external servers or complex configurations are required.
- **🌐 Vercel Ready**: Pre-configured to be deployed seamlessly on Vercel.

---

## 🧠 How It Works

The scoring engine (`scam_detector.py`) uses a weighted keyword and regex-pattern matching algorithm to analyze job postings across several high-risk categories:

1. **💰 Money & Payments**: Requests for security deposits, registration fees, or kit charges.
2. **🤑 Unrealistic Pay**: Outrageous daily or monthly earnings for entry-level roles.
3. **📵 Suspicious Contact**: Hiring exclusively via WhatsApp/Telegram or using generic Gmail addresses.
4. **🏦 Data Abuse**: Unusual requests for Aadhar cards, bank details, or sensitive IDs upfront.
5. **⏳ Artificial Urgency**: Time-pressure tactics like "Act Now", "Limited Seats", or "Immediate Joining".
6. ** pyramid MLM Schemes**: Multi-level marketing red flags like "Be your own boss" and "Refer and earn".

*Scores accumulate based on the severity of the flagged item and are capped at 100.*

---

## 🚀 Installation & Setup

### 1. Prerequisites
- [Python 3.9+](https://www.python.org/downloads/) installed on your machine.
- `pip` (Python package installer)

### 2. Clone the Repository
```bash
git clone https://github.com/sahil24raj/AI-JOB-DETECTOR-python-project.git
cd AI-JOB-DETECTOR-python-project
```

### 3. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```
*The `job_detector.db` database will be automatically initialized using `schema.sql` on the first run.*

### 6. Access the App
Open your favorite browser and navigate to:
**http://127.0.0.1:5000**

---

## 📁 File Structure

```text
AI-JOB-Detector/
├── app.py              # Main Flask application and routing
├── scam_detector.py    # AI scoring engine containing 35+ regex patterns
├── schema.sql          # Database table definitions
├── job_detector.db     # SQLite database (Auto-generated on first run)
├── requirements.txt    # Python package dependencies
├── vercel.json         # Vercel deployment configuration
├── docs/
│   └── screenshots/    # Documentation images and UI previews
├── templates/          # Frontend HTML templates (Jinja2)
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── history.html
└── static/             # Client-side assets (CSS, JS, images)
```

---

## 🔒 Security Measures

- **Password Hashing**: Uses `bcrypt` for industry-standard password encryption.
- **Parameterized Queries**: Prevents SQL injection attacks during database operations.
- **Session Management**: Secure user sessions managed via Flask's secret key.
- **Ephemeral Storage Handling**: Smart routing for `/tmp` database writing to support serverless environments like Vercel.

---

## 🤝 Contributing

Contributions are highly welcome! Whether it's adding new scam detection patterns, improving the UI, or fixing bugs, your help is appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License & Credits

Developed with ❤️ by our amazing team:
- **Sahil Raj** ([@sahil24raj](https://github.com/sahil24raj))
- **Durgesh Mishra** ([@dsr111-cyber](https://github.com/dsr111-cyber))
- **Priyanshu Kumar**  ([@priyanshusingh7758-wq](https://github.com/priyanshusingh7758-wq))

This project is open-source and available under the [MIT License](LICENSE). Feel free to use and modify it for your own purposes!
