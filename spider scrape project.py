import os
import re
import requests
import zipfile
import io
from flask import Flask, render_template_string, request, send_file
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Conditional Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

app = Flask(__name__)

# Single IP Configuration
HOST = '127.0.0.1'
PORT = 5000

FILE_TYPES = {
    "images": [".jpg", ".jpeg", ".png", ".gif"],
    "pdf": [".pdf"],
    "word": [".doc", ".docx"],
    "excel": [".xls", ".xlsx"],
    "contacts": [],
    "all": [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"]
}

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_REGEX = r'\+?\d{1,3}[-. ]?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b'

def get_web_content(url, use_js=False):
    if use_js and SELENIUM_AVAILABLE:
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            content = driver.page_source
            driver.quit()
            return content
        except Exception as e:
            raise Exception(f"Browser error: {str(e)}")
    else:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Request error: {str(e)}")

def extract_contacts(html_content):
    try:
        emails = re.findall(EMAIL_REGEX, html_content, re.IGNORECASE)
        phones = re.findall(PHONE_REGEX, html_content)
        cleaned_phones = [re.sub(r'\D', '', p) for p in phones if 7 <= len(re.sub(r'\D', '', p)) <= 15]
        return {
            "emails": list(set(emails)),
            "phones": list(set(cleaned_phones))
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url'].strip()
        action = request.form['action']
        file_type = request.form.get('file_type', 'all')
        use_js = 'enable_js' in request.form and SELENIUM_AVAILABLE

        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'

        try:
            content = get_web_content(url, use_js)
            
            if action == 'download_page':
                return send_file(
                    io.BytesIO(content.encode()),
                    download_name='webpage.html',
                    as_attachment=True
                )

            elif action == 'download_files':
                if file_type == 'contacts':
                    contacts = extract_contacts(content)
                    if 'error' in contacts:
                        return f"Error: {contacts['error']}"
                    
                    email_content = '\n'.join(contacts['emails']) if contacts['emails'] else 'No emails found'
                    phone_content = '\n'.join(contacts['phones']) if contacts['phones'] else 'No phone numbers found'
                    contact_content = f"Emails:\n{email_content}\n\nPhones:\n{phone_content}"
                    
                    return send_file(
                        io.BytesIO(contact_content.encode()),
                        download_name='contacts.txt',
                        as_attachment=True
                    )

                soup = BeautifulSoup(content, 'html.parser')
                base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                
                resources = set()
                for tag in soup.find_all(['a', 'img', 'link', 'script']):
                    for attr in ['href', 'src']:
                        if tag.has_attr(attr):
                            resource_url = urljoin(base_url, tag[attr])
                            extension = os.path.splitext(urlparse(resource_url).path)[1].lower()
                            if extension in FILE_TYPES.get(file_type, []):
                                resources.add(resource_url)
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for resource in resources:
                        try:
                            response = requests.get(resource, timeout=10)
                            if response.status_code == 200:
                                filename = os.path.basename(urlparse(resource).path)
                                zf.writestr(filename, response.content)
                        except:
                            continue
                zip_buffer.seek(0)
                return send_file(
                    zip_buffer,
                    download_name=f'{file_type}_files.zip',
                    as_attachment=True
                )

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spider Scrape</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: #f0f2f5;
                }
                .container { 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 2.2em;
                }
                input, select, button { 
                    width: 100%; 
                    padding: 12px; 
                    margin: 8px 0; 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                    box-sizing: border-box;
                    font-size: 16px;
                }
                button { 
                    background: #3498db; 
                    color: white; 
                    border: none; 
                    cursor: pointer; 
                    transition: background 0.3s ease;
                }
                button:hover {
                    background: #2980b9;
                }
                .options { 
                    display: none; 
                    margin: 15px 0;
                }
                .js-toggle { 
                    margin: 15px 0;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                .js-toggle input[type="checkbox"] {
                    margin: 0;
                    width: 18px;
                    height: 18px;
                    flex-shrink: 0;
                }
                .js-toggle label {
                    margin: 0;
                    font-size: 0.95em;
                    color: #7f8c8d;
                    line-height: 1.4;
                    cursor: pointer;
                    flex-grow: 1;
                }
                .js-toggle label:hover {
                    color: #3498db;
                }
                @media (max-width: 480px) {
                    .container { 
                        padding: 20px; 
                        margin: 10px;
                    }
                    h1 {
                        font-size: 1.8em;
                    }
                    input, select, button {
                        padding: 10px;
                        font-size: 14px;
                    }
                    .js-toggle {
                        gap: 8px;
                    }
                }
            </style>
            <script>
                function toggleOptions() {
                    const action = document.getElementById('action').value;
                    document.getElementById('fileOptions').style.display = 
                        action === 'download_files' ? 'block' : 'none';
                }
                // Initialize on page load
                window.onload = toggleOptions;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🕷 Spider Scrape</h1>
                <form method="POST">
                    <input type="url" name="url" placeholder="https://example.com" required>
                    
                    <select id="action" name="action" onchange="toggleOptions()">
                        <option value="download_page">Download Web Page</option>
                        <option value="download_files">Download Specific Files</option>
                    </select>
                    
                    <div id="fileOptions" class="options">
                        <select name="file_type">
                            <option value="images">Images</option>
                            <option value="pdf">PDF Documents</option>
                            <option value="word">Word Documents</option>
                            <option value="excel">Excel Files</option>
                            <option value="contacts">Contact Details</option>
                            <option value="all">All Files</option>
                        </select>
                    </div>
                    
                    {% if selenium_available %}
                    <div class="js-toggle">
                        <input type="checkbox" name="enable_js" id="enable_js">
                        <label for="enable_js">Enable JavaScript Rendering for dynamic websites</label>
                    </div>
                    {% endif %}
                    
                    <button type="submit">Start Scraping</button>
                </form>
            </div>
        </body>
        </html>
    ''', selenium_available=SELENIUM_AVAILABLE)

if __name__== '__main__':
    app.run(host=HOST, port=PORT, debug=False)