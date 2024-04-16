import requests
import time

# Define the API endpoint
api_endpoint = "http://127.0.0.1:3000/send-task"
url = "http://127.0.0.1:3000/record"
headers = {'Content-Type': 'application/json'}

# Loop to make the API call 100 times
for j in range(20, 61, 20):
# for j in range(1, 3, 1):
    print("Tasks= ", j)
    for i in range(j):
        # Make the API call
        response = requests.post(api_endpoint, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Check if the request was successful
        if response.status_code == 200:
            print(f"Request {i+1} successful")
        else:
            print(f"Request {i+1} failed with status code: {response.status_code}")
        
        # Wait for 1 second before sending the next request
        time.sleep(0.5)
    time.sleep(j*10)
    response = requests.get(url)
    print('------------------------------------------------\n')
