from flask import Flask, request, send_file
import asyncio
from scraper import fetch_html_async
from analyzer import analyze_seo_and_gbob
from exporter import export_to_web_excel

app = Flask(__name__)

# Hamein alag se index.html file ki zaroorat hi nahi, HTML direct yahan handle hoga
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI SEO & GBOB Automation Tool</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #1e1e1e;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            width: 500px;
            text-align: center;
        }
        h1 { color: #bb86fc; margin-bottom: 20px; }
        textarea {
            width: 100%;
            height: 150px;
            background-color: #2d2d2d;
            color: #fff;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 10px;
            box-sizing: border-box;
            resize: none;
            margin-bottom: 20px;
        }
        button {
            background-color: #bb86fc;
            color: #121212;
            border: none;
            padding: 12px 25px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover { background-color: #9965f4; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI SEO & GBOB Tool</h1>
        <p>Enter your website domains below (one per line):</p>
        <form action="/analyze" method="POST">
            <textarea name="domains" placeholder="example.com&#10;mysite.com"></textarea>
            <br>
            <button type="submit">Analyze & Export Excel</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Bina kisi external file ke direct HTML screen par load ho jayegi
    return HTML_TEMPLATE

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        input_text = request.form.get('domains', '').strip()
        if not input_text:
            return "Please enter at least one domain!", 400
            
        domains = [line.strip() for line in input_text.split('\n') if line.strip()]
        results = []
        
        for domain in domains:
            url = domain if domain.startswith(("http://", "https://")) else f"https://{domain}"
            try:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                html_data = loop.run_until_complete(fetch_html_async(url))
                if html_data:
                    report = analyze_seo_and_gbob(html_data, url)
                    results.append(report)
                else:
                    results.append({"Website URL": url, "Website Title": "Failed to Fetch", "Accepts Guest Posts": "Error"})
            except Exception as inner_e:
                results.append({"Website URL": url, "Website Title": f"Error: {str(inner_e)}", "Accepts Guest Posts": "Error"})
                
        if results:
            excel_file = export_to_web_excel(results)
            return send_file(
                excel_file,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name="SEO_GBOB_Web_Database.xlsx"
            )
        return "No data processed", 400
    except Exception as e:
        return f"Python Error on Analyze Route: {str(e)}"

app = app