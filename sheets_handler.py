import gspread
from gspread_formatting import (
    get_conditional_format_rules,
    format_cell_range,
    Color, 
    TextFormat, 
    CellFormat,
    ConditionalFormatRule,
    BooleanRule,
    BooleanCondition,
    GridRange
)
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
    if os.path.exists('service_account.json'):
        creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPE)
        return gspread.authorize(creds)
    
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

def apply_formatting(worksheet, df_len):
    # 1. Format Header
    header_format = CellFormat(
        backgroundColor=Color(0.9, 0.9, 0.9),
        textFormat=TextFormat(bold=True),
        horizontalAlignment='CENTER'
    )
    format_cell_range(worksheet, 'A1:J1', header_format)
    
    # 2. Conditional Formatting for Sponsorship (Column G)
    rules = get_conditional_format_rules(worksheet)
    rules.clear()
    
    # Likely -> Green
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range('G2:G1000', worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('TEXT_EQ', ['Likely']),
            format=CellFormat(backgroundColor=Color(0.85, 0.93, 0.83))
        )
    ))
    
    # Mentioned -> Yellow
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range('G2:G1000', worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('TEXT_EQ', ['Mentioned']),
            format=CellFormat(backgroundColor=Color(0.99, 0.96, 0.83))
        )
    ))
    
    rules.save()
    
    # Freeze the header row
    worksheet.freeze(rows=1)

def update_spreadsheet(df, spreadsheet_name="Post-MBA Job Listings - Seattle"):
    gc = get_gc_client()
    
    # Pre-process: Convert dates and fill NaNs
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]) or df[col].apply(lambda x: isinstance(x, (date, datetime))).any():
            df[col] = df[col].astype(str)
    df = df.fillna('')
    
    try:
        sh = gc.open(spreadsheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        sh = gc.create(spreadsheet_name)
    
    worksheet = sh.get_worksheet(0)
    
    # Robust Deduplication
    existing_records = worksheet.get_all_records()
    existing_df = pd.DataFrame(existing_records)
    
    if not existing_df.empty and 'job_url' in existing_df.columns:
        # Filter out jobs that already exist based on job_url
        new_jobs = df[~df['job_url'].isin(existing_df['job_url'])]
    else:
        # If sheet is empty or no job_url column, treat all as new
        new_jobs = df
        worksheet.clear()
        worksheet.update('A1', [df.columns.values.tolist()] + df.values.tolist())
        print(f"Initialized sheet with {len(df)} jobs.")
        apply_formatting(worksheet, len(df))
        return

    if not new_jobs.empty:
        worksheet.append_rows(new_jobs.values.tolist(), value_input_option='USER_ENTERED')
        print(f"Added {len(new_jobs)} new unique jobs to the sheet.")
        apply_formatting(worksheet, len(existing_df) + len(new_jobs))
    else:
        print("No new unique jobs to add.")

if __name__ == "__main__":
    if os.path.exists("jobs.csv"):
        df = pd.read_csv("jobs.csv")
        update_spreadsheet(df)
    else:
        print("jobs.csv not found. Run scraper.py first.")
