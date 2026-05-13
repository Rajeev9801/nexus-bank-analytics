# 🏦 Nexus Bank Analytics - Premium Fintech Dashboard

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-v1.0--stable-green.svg)](#)
[![UI Framework](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)

Nexus Bank Analytics is a high-performance, modern fintech desktop application designed for comprehensive banking data analysis, transaction monitoring, and AI-driven insights. Built with a premium CustomTkinter interface, it offers a seamless user experience for financial analysts and administrators.

---

## 📸 Screenshots

> *Placeholder: Add actual screenshots to `assets/screenshots/`*

| **Login Screen** | **Main Dashboard** |
|:---:|:---:|
| ![Login](assets/screenshots/login.png) | ![Dashboard](assets/screenshots/dashboard.png) |

| **Transaction Ledger** | **AI Insights** |
|:---:|:---:|
| ![Transactions](assets/screenshots/transactions.png) | ![AI](assets/screenshots/ai_insights.png) |

---

## ✨ Features

### 💎 Premium User Interface
- **CustomTkinter Dark Theme:** Sleek, modern neon fintech aesthetics.
- **Glassmorphism Cards:** High-contrast stat cards with dynamic neon accents.
- **Animated Sidebar:** Smooth transitions and active tab highlighting.
- **Responsive Layout:** Optimized for various window sizes.

### 📊 Advanced Analytics & Charts
- **Interactive Visuals:** Line charts, Area charts, and Donut charts powered by Matplotlib.
- **Real-time Refresh:** Instant data updates from the background simulator.
- **Financial Trends:** Visualize inflow vs. outflow and bank distribution.

### 👥 User Management (Admin Only)
- **Role-Based Access Control (RBAC):** Separate permissions for ADMIN, ANALYST, and VIEWER.
- **Full CRUD Support:** Create, edit, and delete users via secure modal windows.
- **Activity Tracking:** Monitor login/logout times and device metadata.
- **Security:** SHA-256 password hashing and account deactivation status.

### 🧠 AI Engine
- **Fraud Detection:** Automated flagging of suspicious high-value transactions.
- **Predictive Forecasting:** AI-driven 30-day liquid balance estimation.
- **Smart Insights:** Natural language summaries of account activity.

### 📂 Enterprise Reporting
- **Multi-Format Export:** Generate PDF, CSV, and Excel reports with one click.
- **Automated Seeding:** Self-initializing database with 150+ realistic banking records.

---

## 🛠 Tech Stack

- **Frontend:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), [Pillow](https://python-pillow.org/)
- **Backend:** Python 3.x
- **Database:** SQLite3
- **Visualization:** Matplotlib, Pandas, NumPy
- **Reporting:** ReportLab, OpenPyXL
- **Security:** SHA-256 Hashing

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher installed on your system.

### Setup Guide
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Rajeev9801/nexus-bank-analytics.git
   cd nexus-bank-analytics
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Application:**
   ```bash
   python main.py
   ```

---

## 🔐 Default Credentials

| Role | Username | Password |
|:---:|:---|:---|
| **Admin** | `admin` | `admin123` |

---

## 🏛 Database Architecture

The application uses a thread-safe SQLite implementation with the following schema:
- **`users`**: Secure user profiles, roles, and status.
- **`transactions`**: Comprehensive ledger of all banking activities.
- **`alerts`**: System-generated security and fraud notifications.
- **`login_activity`**: Audit logs for system access.

---

## 🗺 Future Roadmap

- [ ] **Multi-Currency Support:** Global financial analysis.
- [ ] **API Integration:** Connect with real banking APIs for live data.
- [ ] **Cloud Sync:** Synchronize data across multiple devices.
- [ ] **Advanced ML Models:** Enhanced predictive analytics using Scikit-Learn.
- [ ] **Mobile App:** Companion application for iOS and Android.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Author

**Rajeev**
- GitHub: [@Rajeev9801](https://github.com/Rajeev9801)
- Project Link: [https://github.com/Rajeev9801/nexus-bank-analytics](https://github.com/Rajeev9801/nexus-bank-analytics)

---

*Built with ❤️ for the Fintech Community.*
