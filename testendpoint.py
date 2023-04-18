import requests
import time

URL = "https://servers.defrag.racing/"

def test_endpoint():
    try:
        r = requests.get(URL).json()
        return r
    except:
        return {}

if __name__ == "__main__":
    while True:
        try:
            data = test_endpoint()
            if "active" in data:
                if "80.209.233.26:27961" in data["active"]:
                    print("Endpoint is up")
                else:
                    print("Endpoint is down")
            else:
                print("Endpoint is down")
            time.sleep(0.5)
        except Exception as e:
            print(e)
            time.sleep(0.5)