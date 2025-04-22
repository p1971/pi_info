import requests
from datetime import datetime, timedelta

APP_ID = 'tfl_lookup'
APP_KEY = '8bebdd6e6b5e4bc6a4a9d76e9a0a863c'

BASE_URL = "https://api.tfl.gov.uk/Journey/JourneyResults/{from_loc}/to/{to_loc}"
HEADERS = {'Accept': 'application/json'}

def fetch_journey(from_loc, to_loc, date, time, mode=None):
    params = {
        'date': date,
        'time': time,
        'timeIs': 'Departing',
        'app_id': APP_ID,
        'app_key': APP_KEY
    }
    if mode:
        params['mode'] = mode
    
    url = BASE_URL.format(from_loc=from_loc.replace(' ', '%20'), to_loc=to_loc.replace(' ', '%20'))

    try:
        print(f"Calling {url}")
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        response_json = response.json()
        print(response_json)
        return response_json
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Status code: {response.status_code}")
        print(f"Response body:\n{response.text}")
        raise
    except Exception as err:
        print(f"Other error occurred: {err}")
        raise

def format_journey(journey_data):
    output = []
    journey = journey_data['journeys'][0]
    output.append(f"Departs: {journey['startDateTime'][11:16]}")
    output.append(f"Arrives: {journey['arrivalDateTime'][11:16]}")
    for leg in journey['legs']:
        instruction = leg['instruction']['summary']
        departure = leg['departurePoint']['commonName']
        arrival = leg['arrivalPoint']['commonName']
        line = leg.get('routeOptions', [{}])[0].get('name', '')
        output.append(f"{instruction} ({departure} → {arrival}) via {line}")
    return "\n".join(output)

if __name__ == "__main__":
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    time_str = "0800"

    try:
        # Leg 1: King's Cross to Farringdon
        leg1_data = fetch_journey("1000129", "1000080", date_str, time_str, mode="tube")
        leg1_output = format_journey(leg1_data)

        # Leg 2: Farringdon to Canary Wharf
        time_leg2 = (today + timedelta(minutes=15)).strftime("%H%M")
        leg2_data = fetch_journey("1000080", "Canary Wharf", date_str, time_leg2, mode="elizabeth-line")
        leg2_output = format_journey(leg2_data)

        # Combine both
        display_text = "Journey: King's Cross → Canary Wharf via Farringdon\n\n"
        display_text += "[Leg 1]\n" + leg1_output + "\n\n"
        display_text += "[Leg 2]\n" + leg2_output

        # You can now render this to your e-ink display
        print(display_text)

    except Exception as e:
        print(f"Error: {e}")
