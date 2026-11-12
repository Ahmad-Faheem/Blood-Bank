# 🩸 Blood Bank - Blood Management System

A robust, data-validated, and rule-based workflow engine built to handle donor life cycles, patient requests, and real-time inventory threshold compliance using standard clinical principles.

---

### 🚀 Elevator Pitch
> *"This application solves the structural coordination gaps common in manual healthcare logistics by replacing reactive paper logs with an automated workflow engine. It implements precise medical validation checks (like a strict 100-day donor cooldown and cross-matching logic) alongside a preemptive notification subsystem to intercept inventory deficits before they impact critical patient care."*

---

## 🛠️ Problem Space & Core Solution Ideas

### 1. The Donor Recurrence Dilemma (Safe Lifecycles)
* **The Problem:** In manual blood banking systems, tracking individual donor timelines creates a risk of premature donations, which can threaten donor safety.
* **The Solution:** The system enforces a **100-day cooling-off block** built directly into the database validation logic. A user can register to donate, but the platform prevents subsequent registration attempts until the 100-day clinical safety period has passed.

### 2. Standardized Inventory Quantification
* **The Problem:** Non-standard metrics for blood measurements lead to logistical supply calculations that are prone to error.
* **The Solution:** The system digitizes inventory metrics with a strict medical conversion standard: **1 Donor = 1 Unit of Blood &asymp; 500ml**.

### 3. Immediate Deficit & Low-Tier Alerting
* **The Problem:** Discovering a stock shortage only *after* an emergency request arrives introduces dangerous delays in hospital care.
* **The Solution:** The system monitors inventory thresholds in real time. It automatically triggers alerts if stock drops below a **safety limit of 10 units** for any blood group, or if a high-volume request (max 10 units allowed per request) exceeds what is currently available in stock.

### 4. Public Accountability via Moderation
* **The Problem:** Open feedback forms on public health portals frequently attract spam, misleading reviews, or unverified information.
* **The Solution:** Guests can submit reviews without authenticating, but the testimonials pass through a state machine that requires explicit administrator review and approval before publishing to the live homepage.

---

## ⚙️ Feature Matrix

### 👤 User / Donor Portal
* **Security & Authentication:** Complete registration, login, and secure logout workflow. Features an **OTP verification** flow for lost passwords.
* **Profile Management:** Interactive settings dashboard to modify avatars, names, geographic addresses, and personal bios.
* **Transactional Tracking:** A read-only historical timeline of the user's past approved donations and blood requests.
* **Information Dashboards:** Public-facing eligibility criteria checkers and a real-time table of available inventory.

### 👑 Administrative Control Panel
* **Operational Dashboard:** High-level metrics tracking total registered donors, pending medical screenings, and unfulfilled patient requests.
* **Clinical Screening Workspace:** Dedicated interface for checking donor eligibility via medical criteria before moving units into the active inventory.
* **Request Management Desk:** Interface to evaluate incoming orders (1 to 10 units) and match them using a built-in serology compatibility matrix.
* **System Notification Engine:** Central feed that handles live system events:
  * New donor registrations.
  * Incoming patient requests.
  * **Low Inventory Flags** (Stock falls below 10 units).
  * **Stock Deficit Alerts** (Valid requests that exceed current inventory levels).

---

## 💻 Technical Setup & Local Execution Guide

Follow these sequential terminal commands to get your local development server running.

### 1. Environment Procurement
Clone the repository and set up a clean Python virtual environment sandbox and run it safely.
```bash
# Clone the repository
git clone [repo-link]
cd blood-bank-system

# Initialize virtual environment
python -m venv .venv

# Activate the environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Dependency Management
pip install --upgrade pip
pip install -r requirements.txt

# Database Initializations & Migrations
python manage.py makemigrations
python manage.py migrate

# Create an Administrative Account
python manage.py createsuperuser

# Launch the Application Server
python manage.py runserver

```
