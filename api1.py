import requests
import pandas as pd
import json
import datetime
import schedule


# ----Configurations ----
API_URL = "http://api.open-notify.org/iss-now.json"
REPROT_FILE = "iss_location_report.csv"

def fetch_iss_location():
    """Fetches the current ISS location  form the Ope-Notify API"""
    try: 
        response = requests.get(API_URL)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None
    
def generate_report_entry():


