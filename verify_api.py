import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================")
    print("   datastraw CRM - API VERIFICATION TEST SUITE   ")
    print("==================================================")
    
    # 1. Create a ticket (POST /api/tickets)
    print("\n[Test 1] Creating a new ticket (POST /api/tickets)...")
    ticket_payload = {
        "customer_name": "Alice Developer",
        "customer_email": "alice.dev@datastraw.io",
        "subject": "Critical integration mismatch error",
        "description": "Getting a 403 authorization failed when pulling data stream from the main API pipeline. Need assistance to inspect JWT claims."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tickets", json=ticket_payload)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is the Django server running at http://127.0.0.1:8000?")
        sys.exit(1)
        
    print(f"Response status: {response.status_code}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    data = response.json()
    print("Response JSON:", data)
    assert "ticket_id" in data, "Response missing 'ticket_id'"
    assert "created_at" in data, "Response missing 'created_at'"
    
    ticket_id = data["ticket_id"]
    print(f"--> Success! Generated Ticket ID: {ticket_id}")
    
    # 2. List all tickets (GET /api/tickets)
    print("\n[Test 2] Listing all tickets (GET /api/tickets)...")
    response = requests.get(f"{BASE_URL}/api/tickets")
    print(f"Response status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    tickets = response.json()
    print(f"Total tickets in database: {len(tickets)}")
    found_ticket = next((t for t in tickets if t["ticket_id"] == ticket_id), None)
    assert found_ticket is not None, f"Created ticket {ticket_id} not found in listing"
    print(f"--> Success! Ticket {ticket_id} is present in listing. Status: {found_ticket['status']}")
    
    # 3. Test Search (GET /api/tickets?search=Alice)
    print("\n[Test 3] Testing search functionality (GET /api/tickets?search=Alice)...")
    response = requests.get(f"{BASE_URL}/api/tickets", params={"search": "Alice"})
    print(f"Response status: {response.status_code}")
    tickets = response.json()
    print(f"Search results matching 'Alice': {len(tickets)}")
    for t in tickets:
        print(f" - #{t['ticket_id']}: {t['customer_name']} | {t['subject']}")
    assert len(tickets) >= 1, "Expected search results to match the created ticket"
    
    # 4. View single ticket details (GET /api/tickets/{ticket_id})
    print(f"\n[Test 4] Retrieving ticket details (GET /api/tickets/{ticket_id})...")
    response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}")
    print(f"Response status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    details = response.json()
    print("Ticket Details:")
    print(f" - ID: {details['ticket_id']}")
    print(f" - Name: {details['customer_name']}")
    print(f" - Email: {details['customer_email']}")
    print(f" - Subject: {details['subject']}")
    print(f" - Status: {details['status']}")
    print(f" - Notes: {details['notes']}")
    assert details["ticket_id"] == ticket_id
    assert len(details["notes"]) == 0, "Expected notes to be initially empty"
    print("--> Success! Ticket details fetched correctly. Notes are empty as expected.")
    
    # 5. Update Ticket - Status & Add Note (PUT /api/tickets/{ticket_id})
    print(f"\n[Test 5] Updating status and appending a note (PUT /api/tickets/{ticket_id})...")
    update_payload = {
        "status": "In Progress",
        "notes": "Spoke to Alice. We found the issue was caused by an expired signing certificate. Re-issuing credentials now."
    }
    response = requests.put(f"{BASE_URL}/api/tickets/{ticket_id}", json=update_payload)
    print(f"Response status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    update_res = response.json()
    print("Response JSON:", update_res)
    assert update_res["success"] is True
    print("--> Success! Ticket updated successfully.")
    
    # 6. Verify changes (GET /api/tickets/{ticket_id})
    print(f"\n[Test 6] Re-fetching details to verify update (GET /api/tickets/{ticket_id})...")
    response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}")
    assert response.status_code == 200
    details = response.json()
    print("Updated Ticket Details:")
    print(f" - Status: {details['status']} (Expected: In Progress)")
    print(f" - Total Notes: {len(details['notes'])} (Expected: 1)")
    if len(details['notes']) > 0:
        print(f"   Note #1: \"{details['notes'][0]['note_text']}\"")
        
    assert details["status"] == "In Progress", f"Status expected to be 'In Progress', got '{details['status']}'"
    assert len(details["notes"]) == 1, f"Expected 1 note, got {len(details['notes'])}"
    assert details["notes"][0]["note_text"] == update_payload["notes"]
    print("--> Success! Verified that status is updated and notes list matches.")
    
    print("\n==================================================")
    print("   ALL REST API ENDPOINT TESTS COMPLETED SUCCESS  ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
