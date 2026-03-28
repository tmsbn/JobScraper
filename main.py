from scraper import search_jobs
from sheets_handler import update_spreadsheet
import os

def run_pipeline():
    print("Starting Job Scraper Pipeline...")
    
    # 1. Scrape Jobs
    df = search_jobs()
    
    if df.empty:
        print("Pipeline finished: No jobs found.")
        return

    # 2. Upload to Google Sheets
    try:
        update_spreadsheet(df)
        print("Pipeline finished successfully!")
    except Exception as e:
        print(f"Error updating spreadsheet: {e}")
        # Save to local CSV as fallback
        df.to_csv("last_run_jobs.csv", index=False)
        print("Saved results to last_run_jobs.csv as fallback.")

if __name__ == "__main__":
    run_pipeline()
