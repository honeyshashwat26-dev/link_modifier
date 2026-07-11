from flask import Flask, request, redirect, render_template_string
import requests
import os

app = Flask(__name__)

# PASTE YOUR VERIFIED CREDENTIALS DIRECTLY INSIDE THE QUOTES BELOW:
SUPABASE_URL = "https://tnmocggzljtyohjbxssd.supabase.co"
SUPABASE_KEY = "sb_publishable_QZYaIay71I2VvNAEdx2z8Q_5JqoO-lC"

# Setup headers for direct API communication
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Modifier</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f9; text-align: center; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .container { width: 100%; max-width: 400px; background: white; padding: 30px 20px; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); box-sizing: border-box; }
        h2 { color: #333; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #28a745; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { background: #218838; }
        .result { margin-top: 25px; padding: 15px; background: #e2f0d9; border-radius: 8px; word-break: break-all; border: 1px solid #bcd8a7; }
        .result a { color: #1e622b; font-weight: bold; text-decoration: none; font-size: 18px; }
        .error { background:#f8d7da; color:#721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔗 Link Modifier</h2>
        <form method="POST" action="/create">
            <input type="url" name="long_url" placeholder="Paste long link here" required>
            <input type="text" name="custom_name" placeholder="Custom name (e.g., myvideo)" required>
            <button type="submit">Modify & Save Link</button>
        </form>

        {% if result_link %}
        <div class="result">
            <p style="margin:0 0 8px 0; color:#555;">Your Permanent Link:</p>
            <a href="{{ result_link }}" target="_blank">{{ result_link }}</a>
        </div>
        {% endif %}
        
        {% if error %}
        <div class="result error">
            <p style="margin:0;">{{ error }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/create', methods=['POST'])
def create():
    long_url = request.form.get('long_url')
    custom_name = request.form.get('custom_name').strip().lower().replace(" ", "-")
    
    try:
        # Check if custom name already exists
        verify_url = f"{SUPABASE_URL}/rest/v1/links?custom_name=eq.{custom_name}"
        response = requests.get(verify_url, headers=HEADERS)
        
        if response.status_code == 200 and len(response.json()) > 0:
            return render_template_string(HTML_TEMPLATE, error="That name is already taken!")
        
        # Insert data directly via HTTP POST
        insert_url = f"{SUPABASE_URL}/rest/v1/links"
        payload = {"custom_name": custom_name, "original_url": long_url}
        post_response = requests.post(insert_url, headers=HEADERS, json=payload)
        
        if post_response.status_code in [200, 201]:
            domain = request.host_url.replace("http://", "https://")
            result_link = f"{domain}{custom_name}"
            return render_template_string(HTML_TEMPLATE, result_link=result_link)
        else:
            return render_template_string(HTML_TEMPLATE, error=f"Database rejected entry: {post_response.text}")
            
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=f"System error: {str(e)}")

@app.route('/<custom_name>')
def redirect_to_url(custom_name):
    try:
        # Lookup original link
        search_url = f"{SUPABASE_URL}/rest/v1/links?custom_name=eq.{custom_name.lower()}"
        response = requests.get(search_url, headers=HEADERS)
        
        if response.status_code == 200 and len(response.json()) > 0:
            original_url = response.json()[0]["original_url"]
            return redirect(original_url)
    except Exception:
        pass
    return "<h3>Link not found or broken!</h3>", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
