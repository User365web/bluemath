from flask import Flask, render_template, request, jsonify, Response
import math

app = Flask(__name__)


@app.get('/robots.txt')
def robots_txt():
    base = request.url_root.rstrip('/')
    content = f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"
    return Response(content, mimetype='text/plain')

@app.get('/sitemap.xml')
def sitemap():
    base = request.url_root.rstrip('/')
    paths = [
        '/',
        '/faq',
        '/guides',
        '/guides/scientific-calculator-guide',
        '/guides/percentages-and-ratios',
        '/guides/quadratic-equations',
        '/contact',
        '/privacy',
        '/terms',
    ]
    xml_urls = ''.join(f'<url><loc>{base}{path}</loc></url>' for path in paths)
    xml = '<?xml version="1.0" encoding="UTF-8"?>' + '\n' +           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + xml_urls + '</urlset>' + '\n'
    return Response(xml, mimetype='application/xml')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/guides')
def guides():
    return render_template('guides.html')

@app.route('/guides/<slug>')
def guide(slug):
    guides_map = {
        'scientific-calculator-guide': ('How to Use a Scientific Calculator Effectively', 'scientific-calculator-guide.html'),
        'percentages-and-ratios': ('Percentages, Ratios & Proportions: A Practical Guide', 'percentages-and-ratios.html'),
        'quadratic-equations': ('How to Solve Quadratic Equations', 'quadratic-equations.html'),
    }
    item = guides_map.get(slug)
    if not item:
        return render_template('404.html'), 404
    return render_template(item[1], title=item[0])

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.post('/api/contact')
def contact_api():
    data = request.get_json(silent=True) or {}
    name, email, message = data.get('name','').strip(), data.get('email','').strip(), data.get('message','').strip()
    if not name or not email or not message:
        return jsonify({'ok': False, 'message': 'Please complete all fields.'}), 400
    # Demo-only contact endpoint. Connect this to email/database in production.
    return jsonify({'ok': True, 'message': 'Thanks! Your message has been received in demo mode.'})

if __name__ == '__main__':
    app.run(debug=True)
