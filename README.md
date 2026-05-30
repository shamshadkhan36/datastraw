# datastraw Support CRM System

A full-stack, professional Customer Support Ticketing CRM system built as an end-to-end solution for handling customer tickets, internal comments/notes, and team collaboration.

Live, interactive, and responsive, the application utilizes **Full-stack Django** paired with a SQLite database, custom CSS variables for styling, and dynamic Vanilla JavaScript to achieve a single-page application (SPA) responsiveness.

---

## 🛠️ Technology Stack & Architecture

### Core Stack
- **Backend Framework**: Python 3.10 + Django 5.2 (built-in ORM, routing, templates, and security features)
- **Database**: SQLite (2-table design: `tickets` and relational `notes`)
- **Frontend Engine**: Django Templates + Vanilla ES6 JavaScript (no heavyweight JS frameworks or Tailwind CSS required, ensuring raw styling control and lightweight loading)
- **Design & Styling**: Custom Vanilla CSS using HSL color space variables, glassmorphic panels (`backdrop-filter`), hover actions, and fluid responsive layouts (fluid grid/flexbox).

### Architectural Rationale
We chose a **Full-stack Django** model (Option B) to prioritize shipping velocity, single-server deployment ease, and backend/database model cohesion.
To deliver a premium agent experience, we combined the server-side templates with client-side **AJAX Fetch API**:
1. **Search-as-you-type & Filter**: The dashboard loads instantly. When typing in search or clicking filters, JavaScript fetches matching JSON records from `/api/tickets` and rewrites the table DOM dynamically without reloading the entire page. Includes keyword highlighting.
2. **Notes timeline & status switcher**: Inside the ticket details page, status updates and comment submittals are sent asynchronously via `PUT /api/tickets/{ticket_id}`. The timeline appends notes and changes status pills on-the-fly, giving a seamless SPA-like interaction.

---

## 📁 Project Structure

```text
datastraw/
├── manage.py              # Django CLI utility
├── db.sqlite3             # Local SQLite database
├── verify_api.py          # Automated API verification test suite
├── .gitignore             # Git ignored files
├── .env                   # Local environment variables
├── .env.example           # Environment variables configuration template
├── README.md              # Documentation
├── crm_project/           # Configuration directory
│   ├── settings.py        # Project settings (dotenv loaded, static configs)
│   ├── urls.py            # Primary URL Router (includes app URLs)
│   └── wsgi.py
└── tickets/               # Core application logic
    ├── admin.py           # Django Admin panel configurations (tables, inlines, filters)
    ├── models.py          # Database Schemas (Ticket & Note models)
    ├── urls.py            # App-level routing (UI pages and REST APIs)
    ├── views.py           # Controller (HTML renders & REST JSON API handlers)
    ├── static/            # Static assets
    │   ├── css/
    │   │   └── styles.css # Styling system (glowing status badges, glass cards, grids)
    │   └── js/
    │       ├── dashboard.js  # Real-time debounced search & filter handler
    │       └── detail.js     # AJAX status updater & timeline appender
    └── templates/         # HTML Layouts
        └── tickets/
            ├── base.html       # Sidebar shell, clock timer, structural wrapper
            ├── dashboard.html  # Ticket stats cards, search input, filters, table
            ├── create.html     # Customer ticket intake form
            └── detail.html     # Two-column ticket details page + notes timeline
```

---

## ⚙️ Local Installation & Running Guide

Ensure Python 3.10+ is installed on your system.

### 1. Set Up Virtual Environment & Dependencies
Create the environment, activate it, and install required libraries:

```bash
# Create Virtual Environment
python -m venv venv

# Activate Virtual Environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install Django, python-dotenv, and requests
pip install -r requirements.txt
# OR install manually:
pip install django python-dotenv requests
```

### 2. Copy Local Configurations
Copy the environment variables template and customize details if needed:
```bash
cp .env.example .env
```

### 3. Database Migrations
Generate and apply database tables to the SQLite database:
```bash
python manage.py makemigrations
python manage.py migrate
```

*Note: Migrations have already been applied to the local repository, but running migrate is a good safety check.*

### 4. Create Superuser (Optional)
We have pre-created an administrator account for you to access the Django admin portal:
- **Username**: `admin`
- **Password**: `adminpassword`

If you wish to create a custom administrator:
```bash
python manage.py createsuperuser
```

### 5. Run the Local Server
Boot up the Django development server:
```bash
python manage.py runserver
```
The application will load at **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.

---

## 🚀 REST API Mapping & Specifications

| Method | Endpoint | Description | Payload Body (JSON) | Response (JSON) |
|---|---|---|---|---|
| **POST** | `/api/tickets` | Create a new ticket | `{ "customer_name", "customer_email", "subject", "description" }` | `{ "ticket_id", "created_at" }` |
| **GET** | `/api/tickets` | List and search tickets | Query params: `?status=Open&search=query` | `[{ "ticket_id", "customer_name", "subject", "status", "created_at" }]` |
| **GET** | `/api/tickets/{ticket_id}` | Retrieve ticket details + notes | None | `{ "ticket_id", "customer_name", "customer_email", "subject", "description", "status", "created_at", "updated_at", "notes": [...] }` |
| **PUT** | `/api/tickets/{ticket_id}` | Update status or add a note | `{ "status": "In Progress", "notes": "New comment text" }` | `{ "success": true, "updated_at" }` |

---

## 🧪 Automated API Testing

We have built a dedicated test suite `verify_api.py` that hits all endpoints, checks for valid responses, payload formats, and correct DB mutations.

To run the automated API tests:
1. Ensure the server is running (`python manage.py runserver`).
2. Run the verification script:
   ```bash
   python verify_api.py
   ```

*The script will print step-by-step validations confirming that tickets are created, filtered, queried, updated, and that notes are associated correctly.*

---

## ☁️ Deployment Checklist

The application is fully prepared for one-click hosting on platforms like **Render.com** or **Railway.app**:

1. **Procfile**: For Gunicorn, add a `Procfile` at the root:
   ```text
   web: gunicorn crm_project.wsgi:application
   ```
2. **Settings**: The project loads `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` dynamically from environment variables, which can be configured directly inside your hosting dashboard (e.g. `DEBUG=False`).
3. **Static Collection**: Run `python manage.py collectstatic` as part of your deployment build command to compile static CSS and JS resources into the `staticfiles/` directory served by WhiteNoise or a proxy.
