# New Vision Academy - School Website + CMS + Smart Admission System

A complete production-ready school website with Content Management System and AI-powered Admission Management System.

## Features

### Public Website
- Premium responsive design (Desktop, Tablet, Mobile)
- Hero slider, statistics, principal/chairman messages
- Notices, News, Blogs with SEO
- Gallery with albums
- Staff/Teachers directory
- Facilities & What We Offer
- Admission enquiry form
- Contact form
- Global search
- Newsletter subscription
- Floating WhatsApp & Call buttons
- Cookie consent
- Dynamic sitemap & robots.txt
- SEO: Open Graph, meta tags, schema-ready

### Admin Panel
- Dashboard with visitor analytics, charts
- Full school settings (logo, contact, social, SEO)
- Hero slider management
- Notice, News, Blog CRUD
- Gallery albums & media upload
- Staff management
- Facilities management
- Principal & Chairman message editor
- Admission enquiries with status, priority, reply history, CSV export
- Contact messages management
- Newsletter subscribers
- **AI Smart Auto-Reply System**
- Activity logs
- Database backup & download
- Analytics (devices, browsers, popular pages)
- Change password

### AI Auto-Reply System
- Monitors admission enquiries and contact messages
- If no admin reply within configured time (default 3 hours), automatically sends personalized acknowledgement email
- Configurable wait times: 30min, 1h, 2h, 3h, 6h, 12h, 24h
- Editable templates with variables
- Intent detection (admission, fee, general, etc.)
- Full logging of AI actions
- Enable/disable from admin

## Tech Stack
- Python 3.10+ / Flask 3
- SQLite (auto-created)
- Bootstrap 5 + Font Awesome 6
- Jinja2 templates
- Flask-Login, Flask-WTF (CSRF), Flask-Mail
- Pillow (image compression)
- Bleach (XSS protection)

## Installation

```bash
# Clone / extract
cd new_vision_academy

# Create virtualenv (recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
```

Open http://localhost:5000

**Admin Login:** http://localhost:5000/auth/login  
Username: `admin`  
Password: `admin123`

## Production Deployment

### Environment Variables
Copy `.env.example` to `.env` and configure:
- SECRET_KEY
- MAIL_* for SMTP (Gmail, SendGrid, etc.)
- DATABASE_URL (optional, defaults to SQLite)

### Gunicorn (Linux/VPS)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Render.com
- Build: `pip install -r requirements.txt`
- Start: `gunicorn wsgi:app`
- Set environment variables

### Windows Server
```bash
pip install -r requirements.txt
python run.py
# Or use Waitress: waitress-serve --port=8000 wsgi:app
```

## Security
- Password hashing (Werkzeug)
- CSRF protection on all forms
- XSS sanitization (Bleach)
- SQL injection protection (SQLAlchemy ORM)
- Login attempt lockout (5 attempts → 30 min lock)
- Secure session cookies
- Activity audit logs

## Project Structure
```
new_vision_academy/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py
│   ├── models/              # SQLAlchemy models
│   ├── blueprints/
│   │   ├── public/          # Public website
│   │   ├── admin/           # Admin panel
│   │   └── auth/            # Login/logout
│   ├── services/
│   │   └── ai_reply.py      # AI auto-reply worker
│   ├── utils/
│   │   ├── helpers.py
│   │   └── seed.py          # Sample data
│   ├── templates/
│   │   ├── public/
│   │   └── admin/
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/
├── instance/                # DB, backups, logs
├── run.py
├── wsgi.py
├── requirements.txt
└── README.md
```

## Default Credentials
- **Admin:** admin / admin123
- Change password immediately after first login.

## License
Proprietary - New Vision Academy


## GitHub

```bash
git clone <your-repo-url>
cd new_vision_academy
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # edit secrets
python run.py
```

Do **not** commit `.env` or `instance/school.db`.


## Deploy on Render

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Web Service**.
3. Connect the GitHub repo.
4. Settings:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
5. Environment variables (Environment tab):

| Key | Value |
|-----|--------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | (Generate random string) |
| `MAIL_SERVER` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USERNAME` | your Gmail |
| `MAIL_PASSWORD` | Gmail App Password |
| `MAIL_DEFAULT_SENDER` | your Gmail |

6. Click **Create Web Service**.

**Note:** Free Render disk is ephemeral — SQLite data resets on redeploy/restart. For permanent data, add Render **PostgreSQL** and set `DATABASE_URL` from the database connection string.

Admin login after first deploy: `admin` / `admin123` — change password immediately.
