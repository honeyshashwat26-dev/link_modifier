from flask import Flask, request, redirect, render_template_string
from supabase import create_client
import os

app = Flask(__name__)

# Fetch environment variables from Render dashboard
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# IF RENDER FAILS TO READ THE ENVIRONMENT VARIABLES, PASTE YOUR ACTUAL KEYS INSIDE THE QUOTES BELOW AS A BACKUP:
if not SUPABASE_URL:
    SUPABASE_URL = "https://tnmocggzljtyohjbxssd.supabase.co/rest/v1/"
if not SUPABASE_KEY:
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRubW9jZ2d6bGp0eW9oamJ4c3NkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3NjIwMjcsImV4cCI6MjA5OTMzODAyN30.NWiEiSzL_0uLxVzby9c9zZ6z_et2GzVDNIRpwAB_9gk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permanent Link Modifier</title>
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
        check = supabase.table("links").select("original_url").eq("custom_name", custom_name).execute()
        if check.data:
            return render_template_string(HTML_TEMPLATE, error="That name is already taken!")
        
        supabase.table("links").insert({"custom_name": custom_name, "original_url": long_url}).execute()
        
        domain = request.host_url.replace("http://", "https://")
        result_link = f"{domain}{custom_name}"
        return render_template_string(HTML_TEMPLATE, result_link=result_link)
        
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=f"Database error: {str(e)}")

@app.route('/<custom_name>')
def redirect_to_url(custom_name):
    try:
        result = supabase.table("links").select("original_url").eq("custom_name", custom_name.lower()).execute()
        if result.data:
            return redirect(result.data[0]["original_url"])
    except Exception:
        pass
    return "<h3>Link not found or broken!</h3>", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
