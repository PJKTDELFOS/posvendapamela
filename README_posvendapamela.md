# PósVenda — Customer Relationship & Marketing Automation System

> A Django-based CRM and post-sales platform built for small retail businesses — enabling personalized customer engagement, targeted marketing actions, and sales tracking through a single unified interface.

---

## Overview

PósVenda is a full-stack web application designed to replace manual, fragmented post-sales workflows with a centralized system for customer relationship management and direct marketing.

Built for a real retail business, the system handles the full customer lifecycle after the sale: from registering purchase history and customer data to automating personalized outreach — birthday messages, individual discount campaigns, and bulk store announcements — all from a single interface.

---

## Core Features

### 👤 Customer Registry
- Full customer profile management: personal data, contact information, purchase history
- LGPD-compliant data handling — field mapping and compliance checklist included
- Searchable customer database for quick lookup and segmentation

### 🎂 Automated Birthday Campaigns
- Automatic detection of upcoming customer birthdays
- Personalized message dispatch on the customer's birthday date
- Configurable message templates per campaign type

### 🎯 Individual Marketing Actions
- Apply targeted discounts to specific customers for special occasions
- Log and track individual promotional actions per customer
- Full history of actions taken per customer record

### 📢 Bulk Messaging
- Send store announcements and promotional messages to multiple customers simultaneously
- Segment recipients by criteria (purchase history, customer group, etc.)
- Message delivery tracking and status logging

### 💬 Comments & Interaction Log
- Internal notes and comments per customer record
- Interaction history for follow-up and customer service context

---

## Technical Architecture

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Web framework | Django |
| Frontend | HTML5 · CSS3 · Django Templates |
| Database | PostgreSQL |
| Deployment | Google Cloud Platform (App Engine) |
| Configuration | `app.yaml` · `.gcloudignore` |
| Compliance | LGPD — Brazilian Data Protection Law |

### Project Structure

```
posvendapamela/
├── pos_venda/          # Core sales and customer management app
├── posvendasapp/       # Main application config
├── posvendas/          # Supporting business logic
├── comentarios/        # Customer interaction log module
├── base_templates/     # Global HTML templates
├── base_static/        # Static assets (CSS, JS)
├── utils/              # Shared utilities
├── app.yaml            # Google Cloud App Engine config
├── checklist_lgpd.pdf  # LGPD compliance checklist
└── mapeamento_lgpd.txt # LGPD field mapping documentation
```

---

## Data & Compliance

This system handles personal customer data (names, contacts, dates of birth, purchase history) and was built with **LGPD (Lei Geral de Proteção de Dados)** compliance in mind from the start:

- Data field mapping documented (`mapeamento_lgpd.txt`)
- Compliance checklist maintained (`checklist_lgpd.pdf`)
- Minimal data collection principle applied to customer registry

---

## Context & Motivation

This project was built for a real retail client who needed to move away from manual spreadsheets and WhatsApp group messages for post-sales customer management.

The core problem: birthday messages were forgotten, discount campaigns were inconsistent, and there was no central record of which customers had received which promotions. PósVenda solved all three — centralizing customer data, automating date-triggered actions, and providing a full history of every marketing action taken per customer.

---

## Status

Active development. Core CRM and messaging features implemented. Deployed on Google Cloud App Engine.

---

## About

Built by **Albert Pimentel França** — Python Developer and Data Engineer based in Rio de Janeiro, Brazil.

- GitHub: [@PJKTDELFOS](https://github.com/PJKTDELFOS)
- LinkedIn: [albert-pimentel-franca](https://www.linkedin.com/in/albert-pimentel-franca/)
- Open to remote opportunities in Data Engineering, Python Development, and Backend Development

---

## License

© 2026 Albert Pimentel França. All rights reserved.
