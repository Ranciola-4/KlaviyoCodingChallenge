import csv
import requests
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

print("--- Starting Klaviyo Event Sender ---")

# --- Configuration ---
KLAVIYO_PRIVATE_API_KEY = os.getenv("KLAVIYO_PRIVATE_API_KEY")
KLAVIYO_EVENTS_API_URL = "https://a.klaviyo.com/api/events"
CSV_FILE_PATH = "bookingwithnames.csv"
API_REVISION = "2025-07-15"

# --- Main Logic ---

def send_event_to_klaviyo(email, first_name, last_name, fitness_test_type, fitness_level, appointment_date):
    """
    Constructs the event payload and sends it to Klaviyo's Create Event API.

    Args:
        email (str): The email address of the profile.
        first_name (str): The first name of the profile.
        last_name (str): The last name of the profile.
        fitness_test_type (str): The type of fitness test (e.g., "VO2 Max").
        fitness_level (str): The fitness level of the participant (e.g., "Advanced").
        appointment_date (str): The date of the appointment (e.g., "2025-07-20").
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Klaviyo-API-Key {KLAVIYO_PRIVATE_API_KEY}",
        "Revision": API_REVISION
    }

    event_id = str(uuid.uuid4())
    current_timestamp = datetime.now().isoformat() + "Z"

    payload = {
        "data": {
            "type": "event",
            "attributes": {
                "profile": {
                    "data": {
                        "type": "profile",
                        "attributes": {
                            "email": email,
                            "first_name": first_name,
                            "last_name": last_name
                        }
                    }
                },
                "metric": {
                    "data": {
                        "type": "metric",
                        "attributes": {
                            "name": "Booked Fitness Test"
                        }
                    }
                },
                "value": 100,
                "value_currency": "USD",
                "properties": {
                    "Fitness Test Type": fitness_test_type,
                    "Fitness Level": fitness_level,
                    "Appointment Date": appointment_date
                }
            }
        }
    }

    print(f"Attempting to send event for {email}...")
    print(f"DEBUG: JSON Payload for {email}:\n{json.dumps(payload, indent=2)}")
    print("-" * 30)

    try:
        response = requests.post(KLAVIYO_EVENTS_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        if response.status_code == 200:
            print(f"SUCCESS: Event for {email} sent. Status: {response.status_code}")
        elif response.status_code == 202:
            print(f"ACCEPTED: Event for {email} accepted for processing. Status: {response.status_code}")
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error for {email} (Status {e.response.status_code}): {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network/Connection Error for {email}: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred for {email}: {e}")

def process_bookings_csv(file_path):
    """
    Reads the CSV file and calls the send_event_to_klaviyo function for each row.
    """
    print(f"Starting to process bookings from {CSV_FILE_PATH}...")
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Extract data from the CSV row, matching the CSV headers
                email = row.get("email")
                first_name = row.get("first_name") # Get first_name
                last_name = row.get("last_name")   # Get last_name
                fitness_test_type = row.get("fitness_test_type")
                fitness_level = row.get("fitness_level")
                appointment_date = row.get("appointment_date")

                if all([email, first_name, last_name, fitness_test_type, fitness_level, appointment_date]):
                    # Pass arguments to send_event_to_klaviyo in the order its definition expects
                    send_event_to_klaviyo(email, first_name, last_name, fitness_test_type, fitness_level, appointment_date)
                else:
                    print(f"Skipping row due to missing data: {row}. Ensure all required CSV headers are present and lowercase.")
    except FileNotFoundError:
        print(f"CRITICAL ERROR: CSV file not found at '{file_path}'. Please ensure it's in the same directory as the script.")
    except Exception as e:
        print(f"CRITICAL ERROR: An unhandled error occurred while processing the CSV: {e}")

if __name__ == "__main__":
    process_bookings_csv(CSV_FILE_PATH)
    print("--- Finished Processing Events ---")