import requests
import datetime

# ----Configurations ----
API_URL = "http://api.open-notify.org/iss-now.json"

def fetch_iss_location():
    """Fetches the current ISS location from the Open-Notify API"""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def print_iss_location():
    """Fetches and prints ISS location and timestamp"""
    iss_data = fetch_iss_location()

    if iss_data:
        timestamp = datetime.datetime.fromtimestamp(iss_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S UTC')
        latitude = iss_data['iss_position']['latitude']
        longitude = iss_data['iss_position']['longitude']
        ll.append()

        print("📡 ISS Current Location:")
        print(f"  Timestamp : {timestamp}")
        print(f"  Latitude  : {latitude}")
        print(f"  Longitude : {longitude}")
        

# Call the function to print output
print_iss_location()

for i in range(5):
    print_iss_location()

lattitudes = set()
longitudes  = set()





