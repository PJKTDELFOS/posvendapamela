# After-Sales Management System

A production-ready Django web application for managing post-sales customer relationships, built and deployed on Google Cloud Platform. The system handles customer lifecycle management, service tracking, team hierarchies, and LGPD (Brazil's data privacy law) compliance.

---

## Live Deployment

Deployed on **Google Cloud App Engine** (Python 3.12 runtime) with a managed **Cloud SQL PostgreSQL** instance in the `southamerica-east1` region.

---

## Features

- **Customer Management** — Full customer profile lifecycle with contact info, documents, and file attachments
- **After-Sales Tracking** — Log and manage post-sale interactions, comments, and follow-ups
- **Role-Based Access Control** — Hierarchical user permission system (`user_group_level`) restricting access to sensitive data based on team role
- **LGPD Compliance** — Brazilian data privacy law (Lei 13.709/2018) mapped and implemented across all sensitive fields:
  - CPF, phone, and email masking in frontend views
  - Restricted field access by permission level
  - Audit logs for data access and modifications
  - Consent tracking fields
- **Excel Report Export** — Generate downloadable `.xlsx` reports via `openpyxl`
- **Brute-Force Protection** — Login attempt throttling via `django-axes`
- **Image & File Uploads** — Secure file storage with anonymized naming via `Pillow`
- **Secure Secrets Management** — All credentials managed via environment variables using `python-decouple` — zero hardcoded secrets

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2.3 |
| Language | Python 3.12 |
| Database | PostgreSQL (Cloud SQL) |
| Cloud | Google Cloud App Engine |
| WSGI Server | Gunicorn |
| Static Files | WhiteNoise 6.9 |
| Forms | django-crispy-forms + Bootstrap 4 |
| Security | django-axes 8.0 |
| Reports | openpyxl 3.1.5 |
| Image Processing | Pillow 11.2.1 |
| Config | python-decouple |

---

## Project Structure

```
posvendapamela/
├── posvendas/          # Core Django project (settings, URLs, WSGI)
├── pos_venda/          # Main after-sales app (models, views, forms)
├── posvendasapp/       # Extended app logic and business rules
├── comentarios/        # Customer comments and interaction logs
├── utils/              # Shared utilities and helper functions
├── base_templates/     # Global HTML templates
├── base_static/        # Static assets (CSS, JS)
├── app.yaml            # GCP App Engine deployment config
├── requirements.txt    # Python dependencies
├── mapeamento_lgpd.txt # LGPD data mapping documentation
└── checklist_lgpd.pdf  # LGPD implementation checklist
```

---

## Local Setup

### Prerequisites

- Python 3.12+
- PostgreSQL
- Git

### Steps

```bash
# Clone the repository
git clone https://github.com/PJKTDELFOS/posvendapamela.git
cd posvendapamela

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file with required variables
cp .env.example .env
# Edit .env with your local database credentials

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

### Required Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DB_NAME=posvendas
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=posvendas.settings
```

---

## Deployment (Google Cloud App Engine)

```bash
# Authenticate with GCP
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud app deploy app.yaml
```

The `app.yaml` configures:
- Python 3.12 runtime
- Gunicorn as WSGI entrypoint
- Cloud SQL connection
- Forced HTTPS on all routes
- Auto-scaling up to 2 instances
- Static file serving

---

## LGPD Compliance

This system was designed with Brazilian data privacy law (LGPD — Lei 13.709/2018) in mind:

| Data Field | Classification | Implemented Controls |
|---|---|---|
| Full Name | Highly necessary | Restricted access by role level |
| Phone | Critical | Frontend masking `(XX) XXXXX-1234` |
| Email | Critical | Format validation, partial masking in lists |
| CPF | Critical | Frontend masking `XXX.XXX.XXX-12`, format validation |
| Birthday | Necessary | Access restricted by permission level |
| Uploaded Files | Highly necessary | Anonymized file naming, restricted read permissions |

Audit logging is implemented for all sensitive data access, modifications, and deletions.

---

## Security Features

- **django-axes** — Automatic lockout after repeated failed login attempts
- **python-decouple** — No credentials in source code
- **HTTPS enforced** — All HTTP requests redirected via `app.yaml` handlers
- **Hierarchical permissions** — Sensitive fields only accessible to authorized roles
- **LGPD audit trail** — User + timestamp logged on sensitive data events

---

## About the Developer

Built by **Albert Pimentel França** — Software Engineering student and Python developer currently in career transition from 12 years of expertise in public procurement and contract management (B2G), having directly managed over R$104M in government contracts.

Started learning Python and building real projects in April 2024. This system is the result of applying software engineering principles to a domain problem he knows deeply: compliance, data sensitivity, role-based access, and operational auditability in business-critical environments.

- GitHub: [@PJKTDELFOS](https://github.com/PJKTDELFOS)
- LinkedIn: [albert-pimentel](https://www.linkedin.com/in/albert-pimentel-0a47a5338/)
- Open to remote backend/full-stack opportunities in Europe

---

## Roadmap

- [ ] Complete CPF/phone encryption at rest (`django-encrypted-model-fields`)
- [ ] Add LGPD consent management fields
- [ ] Write unit and integration tests (pytest-django)
- [ ] Set up GitHub Actions CI/CD pipeline
- [ ] Rename default branch to `main`
- [ ] Add Docker support for local development

---

## License

This project is private. All rights reserved.
