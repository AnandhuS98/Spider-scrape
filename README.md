🕷️ Spider Scrape – A Secure Web Scraping Application
Spider Scrape is a Python-based web application that allows users to scrape websites for specific content such as images, PDFs, Word/Excel documents, and even contact details like emails and phone numbers. It provides both static and optional JavaScript-rendered scraping using Selenium.

Built with Flask, it features a user-friendly front-end, configurable scraping actions, and secure handling of external requests to ensure safe and controlled data extraction.

🔧 Features
🌐 Web Page Downloader – Download and save the full HTML content of any web page.

📁 File Extractor – Select file types to download (Images, PDFs, Word, Excel).

📇 Contact Scraper – Automatically extract email addresses and phone numbers.

⚙️ JavaScript Rendering (Optional) – Use headless Chrome via Selenium for dynamic websites.

📦 ZIP Output – All resources are downloaded and delivered as a zipped file.

💡 Simple UI – Clean and responsive interface with no external dependencies.

🛡️ Security Highlights
Input validation and http(s) enforcement

Timeout and error handling for web requests

Sanitized file downloads

Safe resource filtering via file extension whitelists

🚀 Tech Stack
Backend: Python, Flask, Requests, BeautifulSoup

Optional: Selenium, WebDriver Manager

Frontend: HTML, CSS (responsive design with plain styles)

Packaging: In-memory Zip creation with zipfile module

📂 How to Run
bash
Copy
Edit
pip install -r requirements.txt
python app.py
Then open http://127.0.0.1:5000 in your browser.

📌 Future Enhancements
Asynchronous scraping (Celery/asyncio)

User login and history tracking

Docker support

URL whitelisting and rate limiting

Progress bar with WebSockets
