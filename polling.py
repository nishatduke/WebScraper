import requests
import schedule


from datetime import datetime, timedelta

EDGAR_API_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"

last_fetch_time = datetime.utcnow() - timedelta(hours=1)

def fetch_new_filings():
    global last_fetch_time
    try:
        response = requests.get(EDGAR_API_URL)
        response.raise_for_status()

        filings = response.json().get('feed', {}).get('entry', [])
        print(filings)
        print(response.json().get("new_feed",{}).get('entry,[]'))
        new_filings = []
        for filing in filings:
            filing_date = datetime.strptime(filing['updated'], '%Y-%m-%dT%H:%M:%SZ')
            if filing_date > last_fetch_time:
                new_filings.append(filing)
            else: 
                new_filings.append(filing)
        last_fetch_time = datetime.utcnow()

        if new_filings:
            for filing in new_filings:
                print(f"Company: {filing['title']}, Filing: {filing['summary']}")
        else:
            print("No new filings found.")

    except requests.RequestException as e:
        print(f"An error occurred while fetching the filings: {e}")

#schedule.every().hour.do(fetch_new_filings)

