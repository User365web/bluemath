# BlueCalc — Scientific Calculator Website

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
- No database required for local use.

## Run on Windows
1. Open Command Prompt/PowerShell in this folder.
2. Create a virtual environment:
   `py -m venv .venv`
3. Activate it:
   PowerShell: `.venv\\Scripts\\Activate.ps1`
   CMD: `.venv\\Scripts\\activate.bat`
4. Upgrade pip:
   `python -m pip install --upgrade pip`
5. Install dependencies:
   `pip install -r requirements.txt`
6. Start the site:
   `python app.py`
7. Open http://127.0.0.1:5000

## Run on macOS/Linux
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `python -m pip install --upgrade pip`
4. `pip install -r requirements.txt`
5. `python app.py`
6. Open http://127.0.0.1:5000

## Important
The contact form is a demo endpoint and does not send email. Before production use, connect `/api/contact` to your preferred email service or database.
