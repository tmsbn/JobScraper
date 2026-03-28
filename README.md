# Post-MBA Job Scraper & Google Sheets Automator

An automated tool designed for MBA graduates to find **non-technical** roles in the **Greater Seattle Area**. It scrapes job listings from multiple sources (LinkedIn, Indeed, Glassdoor, ZipRecruiter), filters for sponsorship-related keywords, and synchronizes the data with a Google Spreadsheet.

## 🚀 Key Features

- **Post-MBA Focus**: Specifically targets roles like Senior Vendor Manager, Category Manager, Program Manager, Strategic Sourcing, and Leadership Development Programs (LDP).
- **Non-Technical Only**: Automatically excludes "Software," "Engineering," "Developer," and "Hardware" roles.
- **Sponsorship Detection**: Identifies and flags potential sponsorship mentions (H1B, Visa, etc.) in a dedicated column.
- **Color-Coding**: Visual cues for sponsorship status (Green for "Likely", Yellow for "Mentioned").
- **Google Sheets Integration**: Automatically creates/updates a spreadsheet named `"Post-MBA Job Listings - Seattle"` with frozen headers.
- **Intelligent Deduplication**: Uses `job_url` as a unique identifier to ensure no duplicate roles are ever posted.
- **Daily Automation**: Pre-configured GitHub Action to run the scrape every day at 1:00 AM PST.

## 🛠️ Project Structure

- `main.py`: The orchestrator that runs the full pipeline (Scrape -> Upload).
- `scraper.py`: Contains the search logic, non-technical filters, and sponsorship detection.
- `sheets_handler.py`: Manages Google Drive/Sheets authentication, spreadsheet creation, and data syncing.
- `requirements.txt`: Python dependencies (`python-jobspy`, `gspread`, `pandas`, etc.).
- `.github/workflows/daily_scrape.yml`: Automation script for GitHub Actions.

## 📋 Prerequisites

1. **Google Cloud Project**:
   - Enable **Google Sheets API** and **Google Drive API**.
   - Create an **OAuth 2.0 Client ID** (Desktop App) for local runs.
   - Create a **Service Account** for automated GitHub runs.
2. **Authorized Email**:
   - In Google Cloud Console, add your Gmail as a **Test User** under "OAuth consent screen".

## 💻 Local Setup & Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tmsbn/JobScraper.git
   cd JobScraper
   ```

2. **Setup Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Add Credentials**:
   - Place your `credentials.json` (from Google Cloud) in the project root.

4. **Run the Scraper**:
   ```bash
   python main.py
   ```
   *Note: On the first run, a browser window will open for you to log in to your Google account.*

## 🤖 GitHub Automation (Daily Run)

To make the script run every day automatically:

1. Go to your GitHub Repository **Settings > Secrets and variables > Actions**.
2. Click **New repository secret**.
3. Name: `GOOGLE_APPLICATION_CREDENTIALS`.
4. Value: Paste the **entire content** of your `service_account.json` file.
5. The script will now run daily and you can also trigger it manually from the **Actions** tab.

## ⚠️ Security
- `credentials.json`, `service_account.json`, and `token.json` are excluded from Git via `.gitignore`.
- **Never** share or commit your private keys.
