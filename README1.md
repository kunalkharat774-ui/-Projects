# 🛡️ SecureWatch — Web Application & API Security Dashboard

**SecureWatch** is a comprehensive, real-time cybersecurity monitoring, analysis, and threat intelligence dashboard designed to protect web applications and APIs. It combines live threat tracking, file security, URL reputation intelligence, system diagnostics, and OWASP alignment into a single intuitive control center.

<p align="center">
  <img src="https://raw.githubusercontent.com/kunalkharat774-ui/-Projects/ba22edd35fa4181e7515042f6c58679db0c13109/SecurityBoard.png" alt="Security Dashboard" width="100%">
</p>

## 🚀 Key Features

### 🌐 1. Live 3D Cyber Attack Map & Real-time Metrics
* **Interactive Globe**: Visualize global cyber attack vectors and live threat trajectories across regions (e.g., US, UK, Brazil, India, China, Russia, Australia).
* **Live KPI Counters**:
  * **Total Requests**: Real-time traffic monitoring ($24.8\text{M}$ requests, $\uparrow 12.5\%$).
  * **Active Threats**: Currently active attack streams ($156$, $\uparrow 8.3\%$).
  * **Vulnerabilities Identified**: Unpatched or monitored vulnerabilities ($28$, $\downarrow 3.7\%$).
  * **Global Risk Score**: Dynamic risk assessment score ($72/100$ - Medium Risk).
* **Attack Status Breakdown**: Track total, successful, blocked, and ongoing cyber attacks.

---

### 🔎 2. URL Reputation Checker
* Instantly verify whether a domain or URL is safe, suspicious, or malicious.
* **Detailed Domain Analytics**:
  * **IP Address & Domain Information**: Host identification and geolocation data.
  * **Reputation Score**: Aggregated safety rating (e.g., $85/100$).
  * **Threat Breakdown**: Real-time evaluation of Phishing, Malware, Spam, and Blacklist status.
* **Scan History**: Maintain continuous logs of recent URL scans, safety categories, and historical scores.

---

### 🔒 3. File Security (Encryption & Decryption)
* **File Encryption**:
  * Drag-and-drop file upload with password-based encryption.
  * Built-in password strength evaluation meter.
  * Instant preparation for secure recipient file sharing.
* **File Decryption**:
  * Upload encrypted files and supply passwords to decrypt on-demand.
* **Recent Activity Logs**: Track file encryption/decryption operations, status, sizes, and timestamps.

---

### 🛡️ 4. Application & API Security Tools
* **Live Attack Map & API Monitoring**: Continuous surveillance of endpoints and backend traffic.
* **Security Alerts & OWASP Top 10 Coverage**: Automated detection aligned with standard web application security risks.
* **Vulnerability & Email Breach Scanner**: Identify credential exposure and software vulnerabilities.
* **Password Strength & IP / Domain Lookup**: On-demand utility toolsets for threat intelligence analysis.

---

### 📊 5. System Health & Performance Monitor
* Real-time telemetry monitoring server system resources:
  * **CPU Usage**: $23\%$
  * **Memory Usage**: $45\%$
  * **Disk Usage**: $31\%$
  * **Network Load**: $68\%$

---

## 🛠️ Dashboard Navigation & Architecture

```text
SecureWatch Control Center
├── 📊 Dashboard (Overview & KPIs)
├── 🗺️ Threat Intelligence
│   ├── Live Attack Map
│   ├── API Monitoring
│   └── Security Alerts
├── 🛡️ Vulnerability Management
│   ├── Vulnerability Scanner
│   ├── OWASP Top 10
│   └── Risk Assessment
├── 🧰 Security Utilities
│   ├── Email Breach Checker
│   ├── Password Strength Tester
│   ├── IP Lookup
│   └── Domain Information
├── 🔗 Content Security
│   ├── URL Reputation Checker
│   └── File Security (Encrypt / Decrypt)
└── ⚙️ System Administration
    ├── Security Logs
    ├── Reports
    ├── User Management
    └── Settings
