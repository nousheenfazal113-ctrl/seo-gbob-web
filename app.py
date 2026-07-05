from flask import Flask, render_template, request, send_file
import asyncio
from scraper import fetch_html_async
from analyzer import analyze_seo_and_gbob
from exporter import export_to_web_excel

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # Agar index.html templates folder mein hai to yeh perfectly chalega
        return render_template('index.html')
    except Exception as e:
        return f"Python Error on Home Route: {str(e)}"

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
                # Vercel serverless friendly async handler
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

# Vercel ko host karne ke liye is line ka global rehna zaroori hai
app = app

