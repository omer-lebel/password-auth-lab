# Attacker Module

This directory contains **educational implementations of automated authentication attacks**,
designed to run **only in a controlled laboratory environment (localhost)**.

The purpose of these scripts is to measure the impact of defensive mechanisms
(such as CAPTCHA simulation) on the **latency and effectiveness of brute-force attacks**.

⚠️ **Warning**  
These scripts are intended for academic use only and must not be used against real systems.

---

## Directory Structure

attacker/
├── burte-force.py
├── Password-Spraying.py
├── users.txt
├── passwords.txt
├── attempts.log
├── log.txt
└── debug.log

---

## 1. Brute Force Attack (`burte-force.py`)

### Description
This script performs a **classic brute-force attack** against a **single target user**.
It systematically attempts a large number of password candidates until either:

- The correct password is found
- A maximum number of attempts is reached
- A maximum runtime limit is exceeded

The attack is optimized using a **persistent HTTP session** and includes detailed
latency measurements for each attempt.

### Key Characteristics
- Targets **one specific username**
- Uses a password dictionary combined with **hybrid variants**
- Logs every attempt with timestamp and latency
- Stops automatically based on attempt count or runtime limits

### Use Case
Used to measure how CAPTCHA and rate-limiting mechanisms affect
high-volume password guessing against a single account.

---

## 2. Password Spraying Attack (`Password-Spraying.py`)

### Description
This script implements a **password spraying attack**, where a small set of common
passwords is tested across **many different user accounts**.

Unlike brute force, this approach minimizes the number of attempts per user
and is commonly used to evade account lockout policies.

### Key Characteristics
- Iterates over **passwords first**, then users
- Tracks successfully compromised accounts
- Enforces global limits on:
  - Maximum number of attempts
  - Maximum runtime
- Produces both summary and debug logs

### Use Case
Used to evaluate whether CAPTCHA activation slows or disrupts
low-and-slow authentication attacks targeting multiple users.

---

## Logging and Measurement

Both attack scripts record detailed timing and result information, including:

- Request latency
- Attempt count
- Success/failure status
- Total attack duration

This data is used to compare:
- Attack performance **with CAPTCHA**
- Attack performance **without CAPTCHA**

---

## Experimental Context

These attack implementations are part of a controlled experiment designed to show that:

- CAPTCHA mechanisms increase attack latency
- CAPTCHA alone does **not fully prevent** automated attacks
- Effective protection requires additional controls such as:
  - Rate limiting
  - Account lockout
  - Multi-factor authentication (MFA)

---

## Legal and Ethical Notice

This code is provided strictly for educational purposes.
Unauthorized use against real systems may be illegal and unethical.
