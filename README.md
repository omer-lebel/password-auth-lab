# 🔐 Password Authentication Lab

An educational research platform for testing password authentication security
against real-world attack scenarios (password spraying and brute-force) with configurable security protections.

> ⚠️ **Disclaimer**
This project is for **educational and research purposes only**. It is designed to demonstrate how different security configurations impact authentication security. 
Do not use these tools against any system you do not have explicit permission to test.

## 📍 Table of Contents
* [📋 Overview](#-overview)
* [🚀 Getting Started](#-getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [🔧 Configuration](#-configuration)
  * [Server Configuration](#server-configuration-configjson)
  * [User Configuration](#user-configuration-usersjson)
* [🧪 Usage](#-usage)
  * [1. Start Server](#1-start-server-)
  * [2. Register Users](#2-register-users-)
  * [3. Run Attack](#3-run-attack-in-different-terminal-)
  * [4. Analyze Results](#4-analyze-results-)
* [📁 Project Structure](#-project-structure)

## 📋 Overview

- **Server**: FastAPI authentication server with multiple hashing algorithms and security protections
- **Client Registrar**: Bulk user registration utility for lab setup
- **Attacker**: Automated attack simulator for password spraying and brute-force
- **Log Analyzer**: Generates PDF security analysis reports

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. **Clone the repository**
```bash
git clone git@github.com:omer-lebel/password-auth-lab.git
cd password-auth-lab
```

2. **Setup virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 🔧 Configuration

### Server Configuration (`config.json`)
This file controls the server's security posture. 
You can toggle hashing algorithms and defensive mechanisms.

```json
{
  "group_seed": 509041496,
  "log_level": "DEBUG",
  "hashing": {
    "type": "argon2",
    "pepper_enable": true,
    "bcrypt_params": { "cost": 12 },
    "argon2_params": { "time": 1, "memory": 131072, "parallelism": 4 }
  },
  "protection": {
    "account_lockout": { "enabled": true, "max_failed_attempts": 10 },
    "rate_limiting": { "enabled": true, "window_seconds": 60, "max_attempt_per_time": 5, "initial_lock_second": 10 },
    "captcha": { "enabled": true, "max_failed_attempts": 3 },
    "totp": { "enabled": true, "max_drift_seconds": 30, "pending_totp_minutes": 3 }
  }
}
```

**Hashing:**
- **Type**: `bcrypt`, `argon2`, `sha256` (with salt), or `debug` (plaintext, testing only)
- **Pepper**: Set `PEPPER` in `server/.env` for additional security layer
- **Parameters**: Tune cost/time/memory for hash functions

**Protection Mechanisms:**
- **Account Lockout**: After `max_failed_attempts` the account will be locked
- **Rate Limiting**: After `max_attempt_per_time` in `window_seconds`, the account will be locked for `initial_lock_second`. Next lockout doubles: 20s, 40s, 80s, ...
- **CAPTCHA**: After `max_failed_attempts`, user gets HTTP 428 and must call `/admin/generate_token/{group_seed}` endpoint to get a token, then retry login with `captcha_token`
- **TOTP 2FA**: Optional two-factor authentication

### User Configuration (`users.json`)
Define the accounts to be registered.
```json
[
  {"username": "tomer",   "password": "bestProjectEver"},
  {"username": "omer",    "password": "100", "totp_secret":  "PVAYEBLEVT4XBE4D7MYV6DNNIOKKHDH5"}
]
```
For TOTP, generate a secret using `pyotp.random_base32()` <br>
Note that TOTP is **optional**

## 🧪 Usage

### 1. Start Server 🖥️
```bash
python -m server.main --config=config.json --output=./results/exp1
```
- `--config`: Configuration JSON file (default: `config.json`)
- `--output`: Output directory for database and logs (default: current directory)

### 2. Register Users 👥
```bash
python users_register/register.py
```
This script reads `users.json` and populates the server database.

### 3. Run Attack *(in different terminal)* ⚔️
Launch simulated attacks using the included dictionary file. Both attack modes utilize `attacker/password.txt`, 
which contains 100,000 common passwords.
```bash
cd attacker
python main.py --attack=<attack type>       
```
Attack Types:
* `brute_force`: Targets **3 specific users**, sequentially. 
* `spray` - Iterates through the dictionary, trying each password across **all registered users** before moving to the next password

both use the dictionary attack from attacker/password.txt

### 4. Analyze Results  📊
```bash
cd log_analyzer
python main.py --input=../results/ex1/attempt.jsonl
```
This generates an `analysis_report.pdf` in the same directory as the input file, detailing:
* Attack success rates and efficiency.
* Time-to-breach metrics.
* Performance impacts of different hashing/protections.

## 📁 Project Structure

```
password-auth-lab/
├── server/             # FastAPI backend & security logic
├── attacker/           # Attack orchestration & scripts
├── log_analyzer/       # PDF report generation
├── users_register/     # Registration utility
├── config.json         # Global server settings
├── users.json          # Target user data
└── requirements.txt    # Project dependencies
```