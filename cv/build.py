#!/usr/bin/env python3
"""
Genera el CV en PDF para cada perfil (Java, PHP, Node.js, Python) y cada idioma (ES, EN).

    python3 cv/build.py            # los 8 PDFs
    python3 cv/build.py java es    # solo uno

Salida: assets/docs/CV_Miguel_Villalba_<Perfil>_<ES|EN>.pdf
Requiere Google Chrome o Chromium (se usa para imprimir el HTML a PDF).

Todo el contenido vive en este archivo. Los hechos (empresas, fechas, tareas)
son comunes; cada perfil solo cambia el titular, el resumen, el orden de las
competencias y qué proyectos se destacan.
"""
import html
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "assets" / "docs"
CSS = (ROOT / "cv.css").read_text(encoding="utf-8")

# ---------------------------------------------------------------- textos fijos
LABELS = {
    "es": {
        "location": "Ñemby, Paraguay · Disponibilidad para trabajo remoto",
        "portfolio": "Portafolio",
        "summary": "Perfil profesional",
        "skills": "Competencias técnicas",
        "experience": "Experiencia profesional",
        "projects": "Proyectos destacados",
        "education": "Formación académica",
        "languages": "Idiomas",
        "courses": "Cursos",
        "extra": "Información adicional",
        "repo": "Repositorio",
        "stack": "Tecnologías",
    },
    "en": {
        "location": "Ñemby, Paraguay · Available for remote work",
        "portfolio": "Portfolio",
        "summary": "Professional Summary",
        "skills": "Technical Skills",
        "experience": "Professional Experience",
        "projects": "Featured Projects",
        "education": "Education",
        "languages": "Languages",
        "courses": "Courses",
        "extra": "Additional Information",
        "repo": "Repository",
        "stack": "Stack",
    },
}

SKILLS = {
    "lang": {"es": "Lenguajes", "en": "Languages"},
    "backend": {"es": "Backend", "en": "Backend"},
    "db": {"es": "Bases de datos", "en": "Databases"},
    "integration": {"es": "Integración", "en": "Integration"},
    "tools": {"es": "Herramientas y entorno", "en": "Tools & environment"},
    "dev": {"es": "Desarrollo", "en": "Development"},
}
SKILL_VALUES_COMMON = {
    "db": {"es": "PostgreSQL, MySQL.", "en": "PostgreSQL, MySQL."},
    "integration": {
        "es": "servicios REST, integración entre sistemas y APIs externas, integración SAP.",
        "en": "REST services, system-to-system and external API integration, SAP integration.",
    },
    "tools": {
        "es": "Docker, Docker Compose, Git, GitLab CI/CD, GitHub Actions, Linux, Apache, Nginx, Postman.",
        "en": "Docker, Docker Compose, Git, GitLab CI/CD, GitHub Actions, Linux, Apache, Nginx, Postman.",
    },
    "dev": {
        "es": "mantenimiento de aplicaciones, lógica de negocio, acceso a datos y resolución de problemas.",
        "en": "application maintenance, business logic, data access and troubleshooting.",
    },
}

SUMMARY_COMMON = {
    "es": "He participado en el desarrollo y mantenimiento de plataformas de importancia institucional, "
          "servicios backend e integraciones entre sistemas. También cuento con experiencia en entornos "
          "productivos, resolución de problemas técnicos y trabajo con equipos de desarrollo.",
    "en": "I have contributed to the development and maintenance of platforms of institutional importance, "
          "backend services and system-to-system integrations, with experience in production environments, "
          "technical troubleshooting and working within development teams.",
}

# ---------------------------------------------------------------- experiencia
def jobs(dev_bullet):
    """dev_bullet: la viñeta de MSPBS que describe con qué tecnologías se desarrolla (varía por perfil)."""
    return [
        {
            "org": {"es": "Ministerio de Salud Pública y Bienestar Social (MSPBS)",
                    "en": "Ministry of Public Health and Social Welfare (MSPBS)"},
            "when": {"es": "Diciembre 2019 – Actualidad · Paraguay", "en": "December 2019 – Present · Paraguay"},
            "role": {"es": "Desarrollador de Sistemas / Backend Developer",
                     "en": "Systems Developer / Backend Developer"},
            "bullets": [
                {"es": "Desarrollo y mantenimiento de sistemas institucionales y servicios backend.",
                 "en": "Develop and maintain institutional systems and backend services."},
                {"es": "Participación en proyectos de alcance nacional, incluyendo VACUNATE y la Línea de Atención 154.",
                 "en": "Contributed to nationwide projects, including VACUNATE (national COVID-19 vaccination platform) and the 154 Helpline."},
                dev_bullet,
                {"es": "Trabajo con APIs, bases de datos relacionales e integración entre sistemas.",
                 "en": "Work with APIs, relational databases and system-to-system integration."},
                {"es": "Participación en la resolución de incidencias y soporte de aplicaciones en entornos productivos.",
                 "en": "Handle incident resolution and application support in production environments."},
                {"es": "Trabajo con PostgreSQL, MySQL, Linux, Docker, Go y herramientas de control de versiones y despliegue.",
                 "en": "Work with PostgreSQL, MySQL, Linux, Docker, Go, version control and deployment tooling."},
            ],
        },
        {
            "org": {"es": "ITTI / ADIGI EAS", "en": "ITTI / ADIGI EAS"},
            "when": {"es": "Mayo 2024 – Abril 2025 · Modalidad remota", "en": "May 2024 – April 2025 · Remote"},
            "role": {"es": "Desarrollador de Software – Backend", "en": "Software Developer – Backend"},
            "bullets": [
                {"es": "Desarrollo y mantenimiento de funcionalidades backend para sistemas de gestión comercial.",
                 "en": "Developed and maintained backend features for commercial management systems."},
                {"es": "Implementación y mantenimiento de APIs e integraciones con servicios externos.",
                 "en": "Implemented and maintained APIs and integrations with external services."},
                {"es": "Integración con SAP y desarrollo utilizando PHP, Laravel y Node.js.",
                 "en": "Built SAP integrations and developed with PHP, Laravel and Node.js."},
                {"es": "Trabajo con bases de datos, pruebas de servicios y despliegues en entornos productivos.",
                 "en": "Worked with databases, service testing and production deployments."},
                {"es": "Colaboración en la resolución de problemas técnicos y evolución de aplicaciones existentes.",
                 "en": "Collaborated on troubleshooting and on the evolution of existing applications."},
            ],
        },
        {
            "org": {"es": "Desarrollo independiente / Freelance", "en": "Independent Development / Freelance"},
            "when": {"es": "Febrero 2018 – Septiembre 2019", "en": "February 2018 – September 2019"},
            "role": {"es": "Desarrollador Full Stack", "en": "Full Stack Developer"},
            "bullets": [
                {"es": "Desarrollo de sistemas de gestión para restaurantes y servicios de agua.",
                 "en": "Built management systems for restaurants and water-supply services."},
                {"es": "Implementación de funcionalidades de ventas, clientes, inventario, movimientos y reportes.",
                 "en": "Implemented sales, customer, inventory, transaction and reporting features."},
                {"es": "Desarrollo backend utilizando Java y Spring.",
                 "en": "Backend development with Java and Spring."},
                {"es": "Implementación de APIs y persistencia de datos con PostgreSQL y MySQL.",
                 "en": "Implemented APIs and data persistence with PostgreSQL and MySQL."},
                {"es": "Desarrollo de interfaces web con JavaScript, HTML y CSS.",
                 "en": "Built web interfaces with JavaScript, HTML and CSS."},
            ],
        },
    ]

# ---------------------------------------------------------------- proyectos
PROJECTS = {
    "springzeus": {
        "title": {"es": "Spring-ZEUS – Sistema de compra-venta", "en": "Spring-ZEUS – Sales & Purchasing System"},
        "sub": {"es": "Java 17 · Spring Boot 3.3 · Spring Security · Spring Data JPA · PostgreSQL · Docker",
                "en": "Java 17 · Spring Boot 3.3 · Spring Security · Spring Data JPA · PostgreSQL · Docker"},
        "bullets": [
            {"es": "API REST protegida con Spring Security: productos, clientes, proveedores, ventas y compras, con roles ADMIN / VENDEDOR.",
             "en": "REST API secured with Spring Security: products, customers, suppliers, sales and purchases, with ADMIN / SELLER roles."},
            {"es": "Actualización automática de stock y anulaciones con reposición; Bean Validation y manejo centralizado de excepciones.",
             "en": "Automatic stock updates and reversals on cancellation; Bean Validation and centralized exception handling."},
        ],
        "repo": "https://github.com/MikeRider27/Spring_Zeus",
    },
    "saiv": {
        "title": {"es": "SAIV Lite 2.0 – Punto de venta e inventario", "en": "SAIV Lite 2.0 – Point of Sale & Inventory"},
        "sub": {"es": "Java 21 · Spring Boot 3.3 · Spring Security (JWT) · JPA · Flyway · PostgreSQL · Angular 18",
                "en": "Java 21 · Spring Boot 3.3 · Spring Security (JWT) · JPA · Flyway · PostgreSQL · Angular 18"},
        "bullets": [
            {"es": "Reescritura web de una aplicación de escritorio Java Swing: caja, ventas, devoluciones, stock, reportes y permisos.",
             "en": "Web rewrite of a Java Swing desktop app: cash register, sales, returns, stock, reports and permissions."},
            {"es": "Autenticación JWT, migraciones con Flyway y despliegue con Docker Compose.",
             "en": "JWT authentication, Flyway migrations and Docker Compose deployment."},
        ],
        "repo": "https://github.com/MikeRider27/SAIVLite",
    },
    "nzps": {
        "title": {"es": "NZ Patient Summary Service", "en": "NZ Patient Summary Service"},
        "sub": {"es": "Java · Spring Boot · HL7 FHIR R4 · GitHub Actions",
                "en": "Java · Spring Boot · HL7 FHIR R4 · GitHub Actions"},
        "bullets": [
            {"es": "Servicio que genera y valida resúmenes de paciente (NZPS/IPS) como Bundles FHIR R4 a partir de JSON simple.",
             "en": "Service that generates and validates patient summaries (NZPS/IPS) as FHIR R4 Bundles from simple JSON."},
            {"es": "Endpoints de validación con OperationOutcome, datos sintéticos, health checks y CI.",
             "en": "Validation endpoints returning OperationOutcome, synthetic data, health checks and CI."},
        ],
        "repo": "https://github.com/MikeRider27/nz-patient-summary",
    },
    "wallet": {
        "title": {"es": "Billetera virtual – Servicios SOAP y REST", "en": "Virtual Wallet – SOAP & REST Services"},
        "sub": {"es": "PHP 8.4 · Laravel 12 · Sanctum · PostgreSQL · Docker (Sail)",
                "en": "PHP 8.4 · Laravel 12 · Sanctum · PostgreSQL · Docker (Sail)"},
        "bullets": [
            {"es": "Servicio SOAP en Laravel como núcleo (capa de negocio, transacciones, bloqueo de saldo, tokens con expiración) y un servicio REST intermedio que lo expone a un cliente React.",
             "en": "Laravel SOAP service as the core (business layer, transactions, balance locking, expiring tokens) plus an intermediate REST service exposing it to a React client."},
            {"es": "Autenticación con API key y Sanctum, excepciones tipadas y aritmética decimal segura para saldos.",
             "en": "API-key and Sanctum authentication, typed exceptions and safe decimal arithmetic for balances."},
        ],
        "repo": "https://github.com/MikeRider27/soap-wallet",
    },
    "ips": {
        "title": {"es": "IPS y VHL – Resumen clínico internacional (MSPBS)", "en": "IPS & VHL – International Patient Summary (MSPBS)"},
        "sub": {"es": "PHP · Laravel · HL7 FHIR · IPS · PostgreSQL · Docker (Sail)",
                "en": "PHP · Laravel · HL7 FHIR · IPS · PostgreSQL · Docker (Sail)"},
        "bullets": [
            {"es": "Aplicación integrada con el servidor FHIR del MSPBS y la red GDHCN/RACSEL: visor de Bundles IPS como ficha clínica y búsqueda de documentos por paciente (ITI-67).",
             "en": "App integrated with the MSPBS FHIR server and the GDHCN/RACSEL network: IPS Bundle viewer rendered as a clinical summary and patient document search (ITI-67)."},
            {"es": "Generación y validación de Virtual Health Links (QR firmado con PIN y expiración); lista blanca de servidores FHIR contra SSRF.",
             "en": "Issuance and validation of Virtual Health Links (signed QR with PIN and expiry); FHIR server allow-list against SSRF."},
        ],
        "repo": "https://github.com/MikeRider27/IPS_VHL",
    },
    "sifen": {
        "title": {"es": "Plataforma de facturación electrónica SIFEN", "en": "SIFEN E-Invoicing Platform"},
        "sub": {"es": "Node.js · NestJS · TypeScript · PostgreSQL (Prisma) · Redis + BullMQ · Docker",
                "en": "Node.js · NestJS · TypeScript · PostgreSQL (Prisma) · Redis + BullMQ · Docker"},
        "bullets": [
            {"es": "Sistema multi-tenant de facturación electrónica integrado con SIFEN (Paraguay): XML, firma XMLDSig y SOAP.",
             "en": "Multi-tenant e-invoicing system integrated with Paraguay's SIFEN: XML, XMLDSig signing and SOAP."},
            {"es": "Auth JWT, roles, API keys, cifrado de certificados y Row-Level Security en PostgreSQL; workers con colas BullMQ.",
             "en": "JWT auth, roles, API keys, encrypted certificates and PostgreSQL Row-Level Security; BullMQ queue workers."},
        ],
        "repo": "https://github.com/MikeRider27/sifen",
    },
    "gideon": {
        "title": {"es": "Gideon – Gestión empresarial con IA", "en": "Gideon – AI-Assisted Business Management"},
        "sub": {"es": "NestJS · TypeScript · PostgreSQL (Prisma) · BullMQ + Redis · React",
                "en": "NestJS · TypeScript · PostgreSQL (Prisma) · BullMQ + Redis · React"},
        "bullets": [
            {"es": "CRM, inventario, ventas y facturación con un asistente de IA que consulta los datos reales del negocio.",
             "en": "CRM, inventory, sales and invoicing with an AI assistant that queries real business data."},
            {"es": "Automatizaciones programadas (alertas de stock, facturas vencidas, reportes) con colas y cron.",
             "en": "Scheduled automations (stock alerts, overdue invoices, reports) using queues and cron."},
        ],
        "repo": "https://github.com/MikeRider27/gideon",
    },
    "aguateria": {
        "title": {"es": "Sistema de gestión para aguatería", "en": "Water Distribution Management System"},
        "sub": {"es": "Node.js · Express · MongoDB (Mongoose) · JWT · React · Docker",
                "en": "Node.js · Express · MongoDB (Mongoose) · JWT · React · Docker"},
        "bullets": [
            {"es": "API REST para clientes, inventario, pedidos, envases retornables, cobros y cierres de caja, con roles.",
             "en": "REST API for customers, inventory, orders, returnable containers, payments and cash closing, with roles."},
        ],
        "repo": "https://github.com/MikeRider27/aguateria",
    },
    "shopmicro": {
        "title": {"es": "ShopMicro – E-commerce con microservicios", "en": "ShopMicro – Microservices E-commerce"},
        "sub": {"es": "Python 3.12 · Flask · SQLAlchemy · PostgreSQL · Redis · pytest · GitHub Actions",
                "en": "Python 3.12 · Flask · SQLAlchemy · PostgreSQL · Redis · pytest · GitHub Actions"},
        "bullets": [
            {"es": "Backend de microservicios Flask (una base por servicio) con JWT, Marshmallow, migraciones Alembic y gateway Nginx.",
             "en": "Flask microservices backend (one database per service) with JWT, Marshmallow, Alembic migrations and an Nginx gateway."},
            {"es": "Rate limiting con Redis, logs estructurados, métricas Prometheus, tests con pytest y CI/CD.",
             "en": "Redis rate limiting, structured logs, Prometheus metrics, pytest tests and CI/CD."},
        ],
        "repo": "https://github.com/MikeRider27/ShopMicro",
    },
    "fintech": {
        "title": {"es": "FinTech – Plataforma de banca digital", "en": "FinTech – Digital Banking Platform"},
        "sub": {"es": "Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 16 · Docker",
                "en": "Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 16 · Docker"},
        "bullets": [
            {"es": "API con cuentas multimoneda, depósitos, retiros, transferencias entre usuarios y estado de cuenta auditable.",
             "en": "API for multi-currency accounts, deposits, withdrawals, user-to-user transfers and auditable statements."},
        ],
        "repo": "https://github.com/MikeRider27/FinTech",
    },
    "roadmap": {
        "title": {"es": "roadmap.sh – Proyectos backend", "en": "roadmap.sh – Backend Projects"},
        "sub": None,
        "bullets": [
            {"es": "Soluciones en Python a los proyectos backend de roadmap.sh, con README de uso, diseño y limitaciones por proyecto.",
             "en": "Python solutions to the roadmap.sh backend projects, each with its own README on usage, design and limitations."},
        ],
        "repo": "https://github.com/MikeRider27/roadmap",
    },
    "apirest": {
        "title": {"es": "API REST – Spring Boot", "en": "REST API – Spring Boot"},
        "sub": None,
        "bullets": [
            {"es": "Servicios para gestión de cuentas, clientes y movimientos.",
             "en": "Services for managing accounts, customers and transactions."},
            {"es": "Reglas de negocio, validaciones, persistencia de datos y generación de reportes.",
             "en": "Business rules, validation, data persistence and report generation."},
        ],
        "repo": "https://github.com/MikeRider27/Apirest-SpringBoot",
    },
    "vacunate": {
        "title": {"es": "VACUNATE – MSPBS", "en": "VACUNATE – MSPBS"},
        "sub": {"es": "Plataforma nacional de agendamiento y gestión de vacunación COVID-19.",
                "en": "National COVID-19 vaccination scheduling and management platform."},
        "bullets": [
            {"es": "Sistema de alcance nacional utilizado por el sistema de salud pública de Paraguay.",
             "en": "Nationwide system used by Paraguay's public health system."},
        ],
        "stack": "PHP · Laravel · MySQL · PostgreSQL",
    },
    "comercial": {
        "title": {"es": "Sistema de gestión comercial – ITTI / ADIGI", "en": "Commercial Management System – ITTI / ADIGI"},
        "sub": None,
        "bullets": [
            {"es": "Gestión de ventas y stock con integración a SAP y APIs de servicios externos.",
             "en": "Sales and stock management with SAP integration and external service APIs."},
        ],
        "stack": "PHP · Laravel · Node.js · MySQL · SAP",
    },
    "linea154": {
        "title": {"es": "Línea de Atención 154 – MSPBS", "en": "154 Helpline – MSPBS"},
        "sub": None,
        "bullets": [
            {"es": "Sistema de atención y telesalud: agendamiento de test, seguimiento de casos y soporte a pacientes.",
             "en": "Telehealth system: test scheduling, case follow-up and patient support."},
        ],
        "stack": "Java · Struts2 · PHP · PostgreSQL",
    },
    "sicam": {
        "title": {"es": "SICAM", "en": "SICAM"},
        "sub": None,
        "bullets": [
            {"es": "Sistema de gestión de calendario y asistencia docente para el sector educativo.",
             "en": "Calendar and teacher-attendance management system for the education sector."},
        ],
        "stack": "PHP · MySQL · JavaScript",
    },
}

# ---------------------------------------------------------------- perfiles
PROFILES = {
    "java": {
        "file": "Java",
        "headline": {"es": "Java Backend Developer | Spring Boot | APIs REST",
                     "en": "Java Backend Developer | Spring Boot | REST APIs"},
        "intro": {
            "es": "Desarrollador Backend y Full Stack con más de 9 años de experiencia profesional en análisis, "
                  "desarrollo, mantenimiento e integración de sistemas. Experiencia trabajando con Java, Spring Boot, "
                  "APIs REST, PostgreSQL y MySQL, además de tecnologías backend complementarias.",
            "en": "Backend and Full Stack Developer with 9+ years of professional experience in the analysis, "
                  "development, maintenance and integration of systems. Hands-on experience with Java, Spring Boot, "
                  "REST APIs, PostgreSQL and MySQL, along with complementary backend technologies.",
        },
        "interest": {
            "es": "Interesado en aportar mis conocimientos de Java y Spring Boot al desarrollo de servicios backend, "
                  "APIs e integraciones, y continuar creciendo técnicamente en equipos colaborativos.",
            "en": "Looking to apply my Java and Spring Boot experience to building backend services, APIs and "
                  "integrations, and to keep growing technically in collaborative teams.",
        },
        "lang": "Java, PHP, JavaScript, Python, Go.",
        "backend": {"es": "Spring Boot, Spring Security (JWT), Spring Data JPA, Flyway, desarrollo de APIs REST; también Laravel y Node.js.",
                    "en": "Spring Boot, Spring Security (JWT), Spring Data JPA, Flyway, REST API development; also Laravel and Node.js."},
        "dev_bullet": {"es": "Desarrollo de funcionalidades y servicios utilizando Java y Spring Boot, además de otras tecnologías del entorno institucional.",
                       "en": "Build features and services with Java and Spring Boot, alongside other technologies in the institutional stack."},
        "projects": ["springzeus", "saiv", "nzps"],
    },
    "php": {
        "file": "PHP",
        "headline": {"es": "PHP Backend Developer | Laravel | APIs REST",
                     "en": "PHP Backend Developer | Laravel | REST APIs"},
        "intro": {
            "es": "Desarrollador Backend y Full Stack con más de 9 años de experiencia profesional en análisis, "
                  "desarrollo, mantenimiento e integración de sistemas. Experiencia con PHP y Laravel en plataformas "
                  "de alcance nacional y sistemas de gestión comercial, APIs REST, integración con SAP, PostgreSQL y MySQL.",
            "en": "Backend and Full Stack Developer with 9+ years of professional experience in the analysis, "
                  "development, maintenance and integration of systems. Experience with PHP and Laravel on nationwide "
                  "platforms and commercial management systems, REST APIs, SAP integration, PostgreSQL and MySQL.",
        },
        "interest": {
            "es": "Interesado en aportar mi experiencia en PHP y Laravel al desarrollo de servicios backend, "
                  "APIs e integraciones, y continuar creciendo técnicamente en equipos colaborativos.",
            "en": "Looking to apply my PHP and Laravel experience to building backend services, APIs and "
                  "integrations, and to keep growing technically in collaborative teams.",
        },
        "lang": "PHP, JavaScript, Java, Python, Go.",
        "backend": {"es": "Laravel (Eloquent, Sanctum), APIs REST y servicios SOAP; también Node.js y Spring Boot.",
                    "en": "Laravel (Eloquent, Sanctum), REST APIs and SOAP services; also Node.js and Spring Boot."},
        "dev_bullet": {"es": "Desarrollo de funcionalidades y servicios con PHP y Laravel (VACUNATE), además de Java y Spring Boot.",
                       "en": "Build features and services with PHP and Laravel (VACUNATE), as well as Java and Spring Boot."},
        "projects": ["wallet", "ips", "vacunate", "comercial"],
    },
    "node": {
        "file": "NodeJS",
        "headline": {"es": "Backend Developer | Node.js · JavaScript | APIs REST",
                     "en": "Backend Developer | Node.js · JavaScript | REST APIs"},
        "intro": {
            "es": "Desarrollador Backend y Full Stack con más de 9 años de experiencia profesional en análisis, "
                  "desarrollo, mantenimiento e integración de sistemas. Experiencia con Node.js en "
                  "integraciones con SAP (ITTI) y proyectos con NestJS, Express y TypeScript: APIs REST, colas, "
                  "multi-tenancy, PostgreSQL y MongoDB.",
            "en": "Backend and Full Stack Developer with 9+ years of professional experience in the analysis, "
                  "development, maintenance and integration of systems. Experience with Node.js on "
                  "SAP integrations (ITTI) and projects built with NestJS, Express and TypeScript: REST APIs, queues, "
                  "multi-tenancy, PostgreSQL and MongoDB.",
        },
        "interest": {
            "es": "Interesado en aportar mi experiencia en Node.js y desarrollo backend a servicios, APIs e "
                  "integraciones, y continuar creciendo técnicamente en equipos colaborativos.",
            "en": "Looking to apply my Node.js and backend experience to services, APIs and integrations, "
                  "and to keep growing technically in collaborative teams.",
        },
        "lang": "JavaScript, TypeScript, PHP, Java, Python, Go.",
        "backend": {"es": "Node.js, NestJS, Express, Prisma, Mongoose, colas con BullMQ, APIs REST; también Laravel y Spring Boot.",
                    "en": "Node.js, NestJS, Express, Prisma, Mongoose, BullMQ queues, REST APIs; also Laravel and Spring Boot."},
        "dev_bullet": {"es": "Desarrollo de funcionalidades y servicios utilizando Java, Spring Boot y otras tecnologías del entorno institucional.",
                       "en": "Build features and services with Java, Spring Boot and other technologies in the institutional stack."},
        "projects": ["sifen", "gideon", "aguateria"],
        "db": "PostgreSQL, MySQL, MongoDB, Redis.",
    },
    "python": {
        "file": "Python",
        "headline": {"es": "Backend Developer | Python · APIs REST | PostgreSQL",
                     "en": "Backend Developer | Python · REST APIs | PostgreSQL"},
        "intro": {
            "es": "Desarrollador Backend y Full Stack con más de 9 años de experiencia profesional en análisis, "
                  "desarrollo, mantenimiento e integración de sistemas. Experiencia con Python en proyectos "
                  "de APIs y microservicios con FastAPI y Flask (SQLAlchemy, Alembic, pytest, CI/CD), además de "
                  "experiencia productiva con Java, PHP, PostgreSQL y MySQL.",
            "en": "Backend and Full Stack Developer with 9+ years of professional experience in the analysis, "
                  "development, maintenance and integration of systems. Hands-on Python experience "
                  "building APIs and microservices with FastAPI and Flask (SQLAlchemy, Alembic, pytest, CI/CD), plus "
                  "production experience with Java, PHP, PostgreSQL and MySQL.",
        },
        "interest": {
            "es": "Interesado en aportar mi experiencia backend al desarrollo de servicios y APIs con Python, "
                  "y continuar creciendo técnicamente en equipos colaborativos.",
            "en": "Looking to apply my backend experience to building services and APIs with Python, "
                  "and to keep growing technically in collaborative teams.",
        },
        "lang": "Python, Java, PHP, JavaScript, Go.",
        "backend": {"es": "FastAPI, Flask, SQLAlchemy, Alembic, Marshmallow, pytest, APIs REST y microservicios; también Spring Boot, Laravel y Node.js.",
                    "en": "FastAPI, Flask, SQLAlchemy, Alembic, Marshmallow, pytest, REST APIs and microservices; also Spring Boot, Laravel and Node.js."},
        "dev_bullet": {"es": "Desarrollo de funcionalidades y servicios utilizando Java, Spring Boot y otras tecnologías del entorno institucional.",
                       "en": "Build features and services with Java, Spring Boot and other technologies in the institutional stack."},
        "projects": ["shopmicro", "fintech", "roadmap"],
        "db": "PostgreSQL, MySQL, Redis.",
    },
}

COURSES = [
    {"es": "Idioma Inglés — Centro de Estudios de Idiomas, Fuerza Aérea (2024)",
     "en": "English language — Language Studies Center, Paraguayan Air Force (2024)"},
    {"es": "Digital Health Systems Coding — Association of Public Health Laboratories (2024)",
     "en": "Digital Health Systems Coding — Association of Public Health Laboratories (2024)"},
    {"es": "Docker for Beginners — KodeKloud (2020)", "en": "Docker for Beginners — KodeKloud (2020)"},
    {"es": "Python Avanzado — Udemy (2019)", "en": "Advanced Python — Udemy (2019)"},
    {"es": "PHP Avanzado — Udemy (2018)", "en": "Advanced PHP — Udemy (2018)"},
]

EDUCATION = {
    "es": ("<p><b>Licenciatura en Análisis de Sistemas Informáticos</b><br>"
           "<small>Universidad Tecnológica Intercontinental (UTIC), Paraguay.</small></p>"
           "<p><b>Ingeniería en Sistemas Informáticos</b><br>"
           "<small>Universidad Tecnológica Intercontinental (UTIC), Paraguay. Materias finalizadas; tesis pendiente.</small></p>"),
    "en": ("<p><b>Bachelor's Degree in Computer Systems Analysis</b><br>"
           "<small>Universidad Tecnológica Intercontinental (UTIC), Paraguay.</small></p>"
           "<p><b>Computer Systems Engineering</b><br>"
           "<small>Universidad Tecnológica Intercontinental (UTIC), Paraguay. All coursework completed; thesis pending.</small></p>"),
}
LANGS = {"es": ["Español: nativo.", "Inglés: nivel intermedio conversacional."],
         "en": ["Spanish: native.", "English: intermediate, conversational."]}
EXTRA = {
    "es": ["Residencia: Paraguay. Disponibilidad: trabajo remoto.",
           "Experiencia en sistemas críticos y entornos productivos."],
    "en": ["Based in Paraguay. Available for remote work.",
           "Experience with mission-critical systems and production environments."],
}


# ---------------------------------------------------------------- render
e = html.escape


def li(items):
    # Literal bullet glyph: Chrome's list markers are not extracted as text, so ATS saw 0 bullets.
    return "".join(f"<li>•&nbsp;{e(i)}</li>" for i in items)


def render(profile_key, lang):
    p = PROFILES[profile_key]
    L = LABELS[lang]

    skills = {
        "lang": p["lang"],
        "backend": p["backend"][lang],
        **{k: v[lang] for k, v in SKILL_VALUES_COMMON.items()},
    }
    if p.get("db"):
        skills["db"] = p["db"]
    skills_html = "".join(
        f"<li><b>{e(SKILLS[k][lang])}:</b> {e(skills[k])}</li>"
        for k in ["lang", "backend", "db", "integration", "tools", "dev"]
    )

    jobs_html = ""
    for j in jobs(p["dev_bullet"]):
        jobs_html += f"""
  <div class="job">
    <div class="job-head"><h3>{e(j['org'][lang])}</h3><span class="when">{e(j['when'][lang])}</span></div>
    <p class="role">{e(j['role'][lang])}</p>
    <ul>{li(b[lang] for b in j['bullets'])}</ul>
  </div>"""

    projects_html = ""
    for key in p["projects"]:
        pr = PROJECTS[key]
        sub = f'<p class="role">{e(pr["sub"][lang])}</p>' if pr.get("sub") else ""
        foot = ""
        if pr.get("repo"):
            short = pr["repo"].replace("https://", "")
            foot = f'<p class="repo">{L["repo"]}: <a href="{pr["repo"]}">{e(short)}</a></p>'
        elif pr.get("stack"):
            foot = f'<p class="repo">{L["stack"]}: {e(pr["stack"])}</p>'
        projects_html += f"""
  <div class="project">
    <div class="job-head"><h3>{e(pr['title'][lang])}</h3></div>
    {sub}
    <ul>{li(b[lang] for b in pr['bullets'])}</ul>
    {foot}
  </div>"""

    title = "CV" if lang == "es" else "Résumé"
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{title} — Miguel Villalba — {e(p['headline'][lang].split('|')[0].strip())}</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>Miguel Villalba</h1>
  <p class="headline">{e(p['headline'][lang])}</p>
  <p class="contact">
    <span>{e(L['location'])}</span>
    <span><a href="mailto:mike.mavc27@gmail.com">mike.mavc27@gmail.com</a></span>
    <span><a href="tel:+595986755760">+595 986 755 760</a></span>
  </p>
  <p class="contact">
    <span>LinkedIn: <a href="https://www.linkedin.com/in/miguel-villalba-673517181">linkedin.com/in/miguel-villalba-673517181</a></span>
    <span>GitHub: <a href="https://github.com/MikeRider27">github.com/MikeRider27</a></span>
  </p>
  <p class="contact">
    <span>{L['portfolio']}: <a href="https://mikerider27.github.io/portafolio/">mikerider27.github.io/portafolio</a></span>
  </p>
</header>

<section>
  <h2>{L['summary']}</h2>
  <p>{e(p['intro'][lang])}</p>
  <p>{e(SUMMARY_COMMON[lang])}</p>
  <p>{e(p['interest'][lang])}</p>
</section>

<section>
  <h2>{L['skills']}</h2>
  <ul class="skills">{skills_html}</ul>
</section>

<section>
  <h2>{L['experience']}</h2>{jobs_html}
</section>

<section>
  <h2>{L['projects']}</h2>{projects_html}
</section>

<section class="edu">
  <h2>{L['education']}</h2>
  {EDUCATION[lang]}
</section>

<section>
  <h2>{L['languages']}</h2>
  <ul>{li(LANGS[lang])}</ul>
</section>

<section>
  <h2>{L['courses']}</h2>
  <ul>{li(c[lang] for c in COURSES)}</ul>
</section>

<section>
  <h2>{L['extra']}</h2>
  <ul>{li(EXTRA[lang])}</ul>
</section>
</body>
</html>"""


def chrome():
    for name in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("No se encontró Google Chrome / Chromium.")


def build(profile_key, lang, browser, tmp):
    src = pathlib.Path(tmp) / f"cv-{profile_key}-{lang}.html"
    src.write_text(render(profile_key, lang), encoding="utf-8")
    pdf = OUT / f"CV_Miguel_Villalba_{PROFILES[profile_key]['file']}_{lang.upper()}.pdf"
    subprocess.run(
        [browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=5000", f"--print-to-pdf={pdf}", src.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"✓ {pdf.relative_to(ROOT.parent)}")


def main(argv):
    profiles = [argv[0]] if argv else list(PROFILES)
    langs = [argv[1]] if len(argv) > 1 else ["es", "en"]
    OUT.mkdir(parents=True, exist_ok=True)
    browser = chrome()
    with tempfile.TemporaryDirectory() as tmp:
        for pk in profiles:
            for lg in langs:
                build(pk, lg, browser, tmp)


if __name__ == "__main__":
    main(sys.argv[1:])
