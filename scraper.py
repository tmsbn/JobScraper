from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import re

def search_jobs():
    # Refined search: Post-MBA roles, specifically excluding technical/engineering roles
    # Adding "Category Manager" and related roles
    search_term = (
        '("MBA" OR "LDP" OR "Leadership Development Program" OR "Senior Vendor Manager" '
        'OR "Senior Program Manager" OR "Senior Category Manager" OR "Senior Product Manager" '
        'OR "Category Manager" OR "Sr Category Manager" OR "Strategic Sourcing Manager" '
        'OR "Supply Chain Manager" OR "Pathways Operations Manager") '
        'NOT "Software" NOT "Engineer" NOT "Developer" NOT "Hardware"'
    )
    
    location = "Seattle, WA"
    
    print(f"Searching for Post-MBA, Category Management, and related roles in {location}...")
    
    jobs = scrape_jobs(
        site_name=["linkedin", "indeed", "glassdoor", "zip_recruiter"],
        search_term=search_term,
        location=location,
        results_wanted=150, # Increased count to capture more related roles
        hours_old=24, 
        country_ahead="USA",
    )
    
    if not jobs.empty:
        # 1. Filter out technical roles
        tech_keywords = ['software', 'engineer', 'developer', 'hardware', 'systems admin', 'it manager']
        jobs = jobs[~jobs['title'].str.contains('|'.join(tech_keywords), case=False, na=False)]
        
        # 2. Identify Sponsorship
        sponsorship_keywords = ['sponsorship', 'h1b', 'visa', 'immigrant', 'eligible to work']
        
        def check_sponsorship(row):
            text = str(row['title']).lower()
            if 'description' in row and pd.notnull(row['description']):
                text += " " + str(row['description']).lower()
            
            if any(k in text for k in ['sponsorship available', 'will sponsor', 'h1-b sponsorship']):
                return "Likely"
            if any(k in text for k in sponsorship_keywords):
                return "Mentioned"
            return "Unknown"

        jobs['sponsorship_status'] = jobs.apply(check_sponsorship, axis=1)
        
        # 3. Select and reorder columns
        cols = ['job_url', 'site', 'title', 'company', 'location', 'date_posted', 'sponsorship_status', 'job_type', 'is_remote']
        available_cols = [c for c in cols if c in jobs.columns]
        jobs = jobs[available_cols]
        
        jobs['scraped_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Found {len(jobs)} filtered Post-MBA and Category Management jobs.")
    else:
        print("No new jobs found.")
        
    return jobs

if __name__ == "__main__":
    df = search_jobs()
    if not df.empty:
        df.to_csv("jobs.csv", index=False)
        print("Jobs saved to jobs.csv")
