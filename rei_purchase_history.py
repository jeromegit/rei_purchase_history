import json
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth


def login(driver, login_url, username, password):
    driver.get(login_url)
    wait = WebDriverWait(driver, 10)
    time.sleep(2)

    # Wait until the email field is visible and interactable
    email_field = wait.until(EC.visibility_of_element_located((By.ID, "logonId")))
    email_field.clear()
    email_field.send_keys(username)

    # Wait until the password field is visible and interactable
    password_field = wait.until(EC.visibility_of_element_located((By.ID, 'password')))
    password_field.clear()
    password_field.send_keys(password)

    # Wait until the Sign In button is clickable
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-analytics-id='login:Sign in']"))
    )
    sign_in_button.click()

    # Wait for the page URL to change, indicating a successful login
    wait.until(EC.url_changes(login_url))
    print(f"Landed on: {driver.current_url}")


# Define a callback function to log requests
def log_request(request):
    print("Request URL:", request['request']['url'])


# Function to create a Selenium WebDriver instance
def create_selenium_driver():
    options = Options()
    #    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_argument("accept-language=en-US,en;q=0.9")
    options.add_argument("referer=https://www.rei.com/")
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.enable', {})

    # Register the callback for requests
    driver.request_interceptor = log_request
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="MacIntel",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    return driver

def main():
    load_dotenv()  # Load environment variables from .env file
    username = os.getenv("REI_USERNAME")
    password = os.getenv("REI_PASSWORD")
    login_url = "https://www.rei.com/login"
    account_url = 'https://www.rei.com/account'
    purchase_history_url = "https://www.rei.com/order-details/rs/purchase-details/history?year=2024"

    driver = create_selenium_driver()

    login(driver, login_url, username, password)

    driver.get(account_url)
    time.sleep(2)
    print(f"Landed on: {driver.current_url}")

    driver.get(purchase_history_url)
    time.sleep(2)
    print(f"Landed on: {driver.current_url}")
    json_data = driver.find_element(By.TAG_NAME, "pre").text
    formatted_json = json.dumps(json_data, indent=4, sort_keys=True)
    print(formatted_json)


if __name__ == "__main__":
    main()
