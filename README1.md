<!-- SecureWatch Banner -->
<div align="center">
  <svg width="100%" height="220" viewBox="0 0 1200 220" fill="none" xmlns="http://www.w3.org/2000/svg" style="background: linear-gradient(135deg, #090B15 0%, #121829 100%); border-radius: 12px; border: 1px solid #1E293B;">
    <circle cx="200" cy="110" r="150" fill="#6366F1" opacity="0.08" filter="blur(50px)"/>
    <circle cx="1000" cy="110" r="150" fill="#EF4444" opacity="0.08" filter="blur(50px)"/>
    <g transform="translate(80, 55)">
      <path d="M50 10 L90 25 V55 C90 80 50 95 50 95 C50 95 10 80 10 55 V25 L50 10 Z" fill="url(#shield-grad)" stroke="#818CF8" stroke-width="3"/>
      <path d="M50 32 L68 42 V58 C68 70 50 78 50 78 C50 78 32 70 32 58 V42 L50 32 Z" fill="#0F172A" stroke="#6366F1" stroke-width="2"/>
      <circle cx="50" cy="53" r="6" fill="#22C55E"/>
    </g>
    <text x="200" y="95" fill="#FFFFFF" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="42" font-weight="800" letter-spacing="1">SecureWatch</text>
    <text x="200" y="130" fill="#94A3B8" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="18" font-weight="500">Web Application & API Security Dashboard</text>
    <text x="200" y="155" fill="#6366F1" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="600">🔴 LIVE THREAT MONITORING  •  3D ATTACK MAP  •  FILE ENCRYPTION</text>
    <g transform="translate(850, 65)">
      <rect x="0" y="0" width="240" height="40" rx="8" fill="#1E293B" stroke="#334155"/>
      <circle cx="20" cy="20" r="6" fill="#22C55E"/>
      <text x="38" y="25" fill="#CBD5E1" font-family="sans-serif" font-size="13" font-weight="600">System Status: </text>
      <text x="135" y="25" fill="#22C55E" font-family="sans-serif" font-size="13" font-weight="700">SECURE</text>
      <rect x="0" y="50" width="240" height="40" rx="8" fill="#1E293B" stroke="#334155"/>
      <circle cx="20" cy="70" r="6" fill="#EF4444"/>
      <text x="38" y="75" fill="#CBD5E1" font-family="sans-serif" font-size="13" font-weight="600">Risk Score: </text>
      <text x="115" y="75" fill="#EAB308" font-family="sans-serif" font-size="13" font-weight="700">72 / 100 (Medium)</text>
    </g>
    <defs>
      <linearGradient id="shield-grad" x1="10" y1="10" x2="90" y2="95" gradientUnits="userSpaceOnUse">
        <stop stop-color="#4F46E5"/>
        <stop offset="1" stop-color="#0F172A"/>
      </linearGradient>
    </defs>
  </svg>
</div>

<br />

# 🛡️ SecureWatch - Web Application & API Security Dashboard

**SecureWatch** is a comprehensive, real-time cyber threat monitoring and security analysis platform designed to safeguard web applications and APIs against modern digital threats.

---

## ✨ Features

### 🌐 Real-Time Cyber Threat Monitoring
* **Live 3D Attack Map:** Interactive visualization of global cyber attacks, tracking total, successful, blocked, and ongoing threats.
* **Metrics Overview:** Instant visibility into Total Requests, Active Threats, Vulnerability Count, and Overall Risk Score.

### 🔍 Security Analysis & Utilities
* **URL Reputation Checker:** Instantly verify if a domain/URL is safe, suspicious, or malicious with detailed analysis (IP Lookup, Phishing/Malware check, Blacklist status).
* **OWASP Top 10 Monitoring:** In-depth scanning aligned with industry security standards.
* **API & Live Monitoring:** Continuous health and threat monitoring for REST APIs.

### 🔐 File Security (Encryption & Decryption)
* **File Encryption:** Password-protect sensitive documents (e.g., PDFs, spreadsheets) before sharing.
* **File Decryption:** Securely decrypt files using custom passphrases directly within the interface.

### 📊 System Status & Logs
* **System Resource Metrics:** Real-time tracking of CPU, Memory, Disk, and Network utilization.
* **Activity Tracking:** Comprehensive logs for recent URL scans and file encryption activities.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript / React / Next.js
* **UI Components & Styling:** Custom Dark Mode / Neon UI Theme, FontAwesome / Lucide Icons
* **Data Visualization:** Three.js / Globe.gl (for 3D Live Attack Map), Chart.js
* **Security & Cryptography:** AES Encryption, Web Crypto API

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Node.js and npm/yarn installed.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/secure-watch.git](https://github.com/your-username/secure-watch.git)
   cd secure-watch
