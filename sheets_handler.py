import gspread
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import os
import pickle
from datetime import datetime, date

# Define the scope
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_gc_client():
    # 1. Try Service Account (Best for GitHub Actions / Automation)
    if os.path.exists('service_account.json'):
        creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPE)
        return gspread.authorize(creds)
    
    # 2. Try OAuth 2.0 (Best for local development / your credentials.json)
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists('credentials.json'):
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPE)
            creds = flow.run_local_server(port=0)
        else:
            raise FileNotFoundError("Neither service_account.json nor credentials.json found.")
            
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    return gspread.authorize(creds)

def update_spreadsheet(df, spreadsheet_name="Post-MBA Job Listings - Seattle"):
    gc = get_gc_client()
    
    # Pre-process DataFrame: Convert all dates to strings for JSON serialization
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]) or df[col].apply(lambda x: isinstance(x, (date, datetime))).any():
            df[col] = df[col].astype(str)
    
    # Fill NaN values with empty strings
    df = df.fillna('')
    
    try:
        sh = gc.open(spreadsheet_name)
        print(f"Opening existing spreadsheet: {spreadsheet_name}")
    except gspread.exceptions.SpreadsheetNotFound:
        sh = gc.create(spreadsheet_name)
        print(f"Created new spreadsheet: {spreadsheet_name}")

    worksheet = sh.get_worksheet(0)
    
    # Get existing data for deduplication
    data = worksheet.get_all_records()
    existing_data = pd.DataFrame(data)
    
    if not existing_data.empty and 'job_url' in existing_data.columns:
        # Deduplicate based on job_url
        new_jobs = df[~df['job_url'].isin(existing_data['job_url'])]
    else:
        new_jobs = df
        # Initialize headers if sheet is empty or only headers exist
        worksheet.clear()
        headers = df.columns.values.tolist()
        values = df.values.tolist()
        worksheet.update('A1', [headers] + values)
        print(f"Initialized sheet with {len(df)} jobs.")
        return

    if not new_jobs.empty:
        # Append only new jobs
        worksheet.append_rows(new_jobs.values.tolist(), value_input_option='USER_ENTERED')
        print(f"Added {len(new_jobs)} new unique jobs to the sheet.")
    else:
        print("No new unique jobs to add.")

if __name__ == "__main__":
    if os.path.exists("jobs.csv"):
        df = pd.read_csv("jobs.csv")
        update_spreadsheet(df)
    else:
        print("jobs.csv not found. Run scraper.py first.")
