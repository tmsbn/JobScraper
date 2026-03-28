from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime

def search_jobs():
    search_term = '"Vendor Manager" OR "Program Manager" OR "Category Manager" OR "Product Manager" OR "Supply Chain Manager"'
    location = "Seattle, WA"
    
    print(f"Searching for jobs in {location}...")
    
    jobs = scrape_jobs(
        site_name=["linkedin", "indeed", "glassdoor", "zip_recruiter"],
        search_term=search_term,
        location=location,
        results_wanted=50,
        hours_old=24, # Only get jobs from the last 24 hours for daily runs
        country_ahead="USA",
    )
    
    if not jobs.empty:
        # Select relevant columns
        jobs = jobs[['job_url', 'site', 'title', 'company', 'location', 'date_posted', 'job_type', 'is_remote']]
        jobs['scraped_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Found {len(jobs)} new jobs.")
    else:
        print("No new jobs found.")
        
    return jobs

if __name__ == "__main__":
    df = search_jobs()
    if not df.empty:
        df.to_csv("jobs.csv", index=False)
        print("Jobs saved to jobs.csv")
