from utilities import ascii_qr
import requests
import time

SERVER_URL = "http://server.novodo.co.uk:2000"

def main():
    print("Starting login process...")

    resp = requests.get(f"{SERVER_URL}/start_login")
    resp.raise_for_status()
    data = resp.json()

    login_url = data["login_url"]
    state = data["state"]

    qr_image = ascii_qr(login_url)
    print(f"Visit: {login_url} to complete login. Scan the QR code below:")
    print(qr_image)

    print("Waiting for you to complete login in browser...")
    while True:
        status_resp = requests.get(f"{SERVER_URL}/login_status/{state}")
        status_resp.raise_for_status()
        status_data = status_resp.json()

        if status_data["status"] == "success":
            user = status_data["user"]
            print(f"Login successful! Hello, {user['login']} ({user['name']})")
            print(f"Profile URL: {user['html_url']}")
            print(f"Avatar URL: {user['avatar_url']}")
            break
        elif status_data["status"] == "failed":
            print("Login failed.")
            break
        else:
            print("Waiting...", end="\r")

        time.sleep(1)

if __name__ == "__main__":
    main()
