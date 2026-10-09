# BlueMath — Scientific Calculator Website

A responsive scientific calculator website built with Python Flask and vanilla JavaScript.

## Features
- Scientific calculator: trig, inverse trig, logs, ln, powers, roots, factorial, constants, percentages, memory and history.
- DEG/RAD angle mode.
- Keyboard input and calculator buttons.
- Quadratic equation solver.
- Statistics calculator (mean, median, min, max, standard deviation).
- Percentage calculator.
- Length, mass, temperature and area unit conversion.
- FAQ, Contact, Privacy Policy and Terms pages.
- Guides/blog section with three practical math articles.
- White and blue responsive design.
- Private admin inbox for contact messages: sign in, view messages, filter unread, mark read/unread, and delete.
- Contact messages are stored in a database.
- Sitemap at `/sitemap.xml` and crawler rules at `/robots.txt`.

## Run locally on Windows
1. Open Command Prompt/PowerShell in this folder.
2. Create a virtual environment: `py -m venv .venv`
3. Activate it: PowerShell `.venv\\Scripts\\Activate.ps1`; CMD `.venv\\Scripts\\activate.bat`.
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Set admin credentials and a stable secret in the same terminal before starting the app. In PowerShell:
   ```powershell
   $env:ADMIN_USERNAME = "choose-a-username"
   $env:ADMIN_PASSWORD = "use-a-long-unique-password"
   $env:SECRET_KEY = "replace-with-a-long-random-secret"
   python app.py
   ```
6. Open `http://127.0.0.1:5000`.
7. Admin inbox: `http://127.0.0.1:5000/admin`.

SQLite is used locally by default and stored in `instance/bluemath.db`.

## Deploy on Render
Keep your existing Web Service and build/start commands. Build command:
`pip install -r requirements.txt`

Start command:
`gunicorn app:app`

In the Render Web Service's **Environment** settings, set:
- `ADMIN_USERNAME` — your private admin username.
- `ADMIN_PASSWORD` — a long, unique password. Do not put it in source code or share it.
- `SECRET_KEY` — a long, random secret value. Keep it private and stable between deployments.
- `COOKIE_SECURE` — `true` for the HTTPS production site.
- `DATABASE_URL` — connection URL for a persistent PostgreSQL database.

### Important: configure persistent database storage
Render's free web-service filesystem is ephemeral. If you leave `DATABASE_URL` unset in production, this app falls back to SQLite, and messages can be lost when the service restarts or redeploys. To keep messages safely across deployments, create/use a persistent PostgreSQL database (for example, a managed PostgreSQL provider), copy its connection URL into the Render `DATABASE_URL` environment variable, and redeploy. The app accepts standard `postgres://` and `postgresql://` connection URLs.

Once deployed, open `https://YOUR-SITE.onrender.com/admin`, sign in with the environment credentials, and review contact submissions there. The `/admin` pages are not listed in the sitemap and are disallowed in `robots.txt`; the actual protection is the login requirement.

## Notes
- Do not commit admin credentials or `SECRET_KEY` into GitHub.
- If you change database providers, preserve the database containing your existing messages.
- The app creates its contact-message table automatically when it starts.
