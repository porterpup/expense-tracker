#!/usr/bin/env python3
"""
OpenSky Flight Data Fetcher (Revised)
Fetches real flight data directly without subprocess
"""

import os
import csv
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip3 install requests")
    exit(1)

# Load credentials from .env
load_dotenv()

OPENSKY_USERNAME = os.getenv('OPENSKY_USERNAME')
OPENSKY_PASSWORD = os.getenv('OPENSKY_PASSWORD')

OPENSKY_API_URL = "https://opensky-network.org/api"

# Airlines of interest (ICAO codes)
AIRLINES = {
    'UAL': 'United',
    'AAL': 'American',
    'DAL': 'Delta'
}

# Major US domestic airports
AIRPORTS = ['KJFK', 'KLAX', 'KORD', 'KDFW', 'KATL', 'KDEN', 'KSFO', 'KLAS']

def fetch_flight_data(days_back=28):
    """
    Fetch flight arrival data from OpenSky
    Returns list of flight records with delays
    """
    
    if not OPENSKY_USERNAME or not OPENSKY_PASSWORD:
        print("ERROR: OpenSky credentials not found in .env")
        return []
    
    auth = (OPENSKY_USERNAME, OPENSKY_PASSWORD)
    flights = []
    
    print(f"\nFetching {days_back} days of flight data from OpenSky...")
    print(f"Airports: {', '.join(AIRPORTS)}")
    print()
    
    for day_offset in range(days_back):
        date = datetime.utcnow() - timedelta(days=day_offset)
        start_time = int(date.replace(hour=0, minute=0, second=0).timestamp())
        end_time = int(date.replace(hour=23, minute=59, second=59).timestamp())
        
        print(f"[{date.date()}] ", end="", flush=True)
        
        day_flights = 0
        
        for airport in AIRPORTS:
            try:
                # Query arrivals for this airport on this day
                response = requests.get(
                    f"{OPENSKY_API_URL}/flights/arrival",
                    params={
                        'airport': airport,
                        'begin': start_time,
                        'end': end_time
                    },
                    auth=auth,
                    timeout=15
                )
                
                if response.status_code == 200:
                    arrivals = response.json()
                    
                    if arrivals:
                        for flight in arrivals:
                            callsign = flight.get('callsign', '').strip()
                            airline_code = callsign[:3] if callsign else None
                            
                            # Only keep our target airlines
                            if airline_code in AIRLINES:
                                # Extract useful fields
                                try:
                                    first_seen = flight.get('firstSeen')
                                    last_seen = flight.get('lastSeen')
                                    est_dep = flight.get('estDepartureAirport')
                                    est_arr = flight.get('estArrivalAirport')
                                    
                                    if first_seen and last_seen and est_dep and est_arr:
                                        # Calculate delay (rough: last_seen - first_seen)
                                        delay_minutes = (last_seen - first_seen) / 60
                                        is_delayed = 1 if delay_minutes > 15 else 0
                                        
                                        flights.append({
                                            'date': date.date().isoformat(),
                                            'flight_id': callsign,
                                            'airline': AIRLINES[airline_code],
                                            'origin': est_dep,
                                            'destination': est_arr,
                                            'scheduled_time': first_seen,
                                            'actual_time': last_seen,
                                            'delay_minutes': round(delay_minutes, 1),
                                            'is_delayed': is_delayed
                                        })
                                        day_flights += 1
                                except Exception:
                                    pass
                    
                elif response.status_code == 429:
                    print("(rate limited)", end="", flush=True)
                    break
                elif response.status_code == 401:
                    print("(auth error)", end="", flush=True)
                    break
            
            except requests.Timeout:
                pass
            except Exception:
                pass
        
        print(f" {day_flights} ✓")
    
    return flights


def save_flights_csv(flights, output_file='opensky_flights_recent.csv'):
    """Save flights to CSV"""
    if not flights:
        print("\nNo flights fetched. Check API access or credentials.")
        return False
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'date', 'flight_id', 'airline', 'origin', 'destination',
            'scheduled_time', 'actual_time', 'delay_minutes', 'is_delayed'
        ])
        writer.writeheader()
        writer.writerows(flights)
    
    print(f"\n✓ Saved {len(flights)} flights to {output_file}")
    
    # Print stats
    delayed = sum(1 for f in flights if f['is_delayed'])
    on_time = len(flights) - delayed
    
    print("\nData Summary:")
    print(f"  On-time: {on_time} ({on_time/len(flights)*100:.1f}%)")
    print(f"  Delayed: {delayed} ({delayed/len(flights)*100:.1f}%)")
    print(f"  Avg delay: {sum(f['delay_minutes'] for f in flights) / len(flights):.1f} min")
    
    return True


def main():
    flights = fetch_flight_data(days_back=28)
    if flights:
        return save_flights_csv(flights, 'opensky_flights_recent.csv')
    return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
