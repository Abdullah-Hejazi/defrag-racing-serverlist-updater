import requests
import time

URL = "https://servers.defrag.racing/"

def test_endpoint():
    response = requests.get(URL)
    if response.status_code == 502:
        return False

    return True

if __name__ == "__main__":
    while True:
        if test_endpoint():
            pass
        else:
            print("Endpoint is down")
        time.sleep(1)