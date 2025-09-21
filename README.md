# 📖 Django Full-Stack Wordle Application Setup

This project implements a secure, stateful Wordle clone built using Django (Python) for the backend and database logic, with integrated HTML/CSS/JavaScript for the frontend user interface.

## 🚀 1. Prerequisites

Ensure you have the following installed on your system:

* **Python 3.8+**
* **pip** (Python package installer)

---

## 🛠️ 2. Project Installation

Follow these steps to set up your environment and install dependencies.

1.  **Create and Activate Virtual Environment:**
    ```bash
    # Create the environment
    python -m venv env 
    # Activate (Linux/macOS)
    source env/bin/activate
    # Activate (Windows)
    .\env\Scripts\activate
    ```

2.  **Install Django:**
    ```bash
    pip install django
    ```

---

## 🗃️ 3. Database and Data Initialization

These steps set up the database tables and load the initial game words.

### 3.1. Database Setup

Run the migrations to create all database tables (`CustomUser`, `WordList`, `UserGuessHistory`, etc.).

```bash
# 1. Create migration files
python manage.py makemigrations game

# 2. Apply migrations (creates all database tables)
python manage.py migrate
3.2. Prepare and Load Word List
Create words.txt: In the root directory (wordle_project/), create a file named words.txt. Fill it with your list of 5-letter words (one word per line).

Run Custom Population Command: This loads the words into the WordList table.

Bash

python manage.py populate_words
3.3. Create Administrator Account (Superuser)
You must run this command to create the initial admin user account for login and dashboard access:

Bash

python manage.py createsuperuser
▶️ 4. Running the Application
Start the local development server:

Bash

python manage.py runserver
