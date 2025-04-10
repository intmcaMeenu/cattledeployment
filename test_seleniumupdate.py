import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import easygui
from webdriver_manager.chrome import ChromeDriverManager

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)  # Print to console for debugging
    return log_entry

# Set up the WebDriver using webdriver_manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the log file
log_file_path = "test/selenium_profile_update_test_results.txt"
with open(log_file_path, "w") as log_file:
    try:
        log_message("Starting the Selenium profile update test...")

        driver.maximize_window()
        log_message("Browser window maximized.")

        # Navigate to the login page and login
        driver.get("http://127.0.0.1:8000/user/login/")
        log_message("Navigated to the login page.")

        # Wait for the email input field to be present
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        log_message("Email input field is visible.")
        email_input.send_keys("ashmianees12@gmail.com")
        log_message("Entered email: ashmianees12@gmail.com")

        # Wait for the password input field to be present
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        log_message("Password input field is visible.")
        password_input.send_keys("Ashmi@12")  # Replace with the actual password
        log_message("Entered password: *********")

        # Wait for the login button to be clickable
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "submit"))
        )
        login_button.click()
        log_message("Clicked the login button.")

        # Wait for the page to load after login
        WebDriverWait(driver, 20).until(EC.title_contains("CattleCare"))
        log_message("Page loaded after login attempt.")

        # Navigate to the user dashboard (profile update page)
        driver.get("http://127.0.0.1:8000/user/user_dashboard/")
        log_message("Navigated to the user dashboard.")

        # Click on "Profile Management" to expand the submenu
        profile_management = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "profileManagement"))
        )
        profile_management.click()
        log_message("Clicked on 'Profile Management' to expand submenu.")

        # Wait for the submenu to appear
        profile_submenu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "profileSubMenu"))
        )
        log_message("Profile submenu is visible.")

        # Click on the "Profile Update" link
        profile_update = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Profile Update"))
        )
        profile_update.click()
        log_message("Clicked on 'Profile Update'.")

        # Wait for the house name input field to be visible
        house_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "house_name"))
        )
        log_message("House name input field is visible.")

        # Clear the existing value and enter the new house name
        house_name_input.clear()
        house_name_input.send_keys("Kattiis House")
        log_message("Updated house name to 'Kattiis House'.")

        # Submit the form (assuming a button with class 'button' for submission)
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".button"))
        )
        submit_button.click()
        log_message("Clicked the submit button to save changes.")

        # Wait for confirmation or page redirect after updating profile
        WebDriverWait(driver, 20).until(EC.url_contains("user_dashboard"))
        log_message("Profile updated successfully!")

        easygui.msgbox("Profile Update Test Passed..!!!")

    except Exception as e:
        log_message(f"An error occurred: {e}")
        easygui.msgbox(f"An error occurred: {e}")

    finally:
        # Close the browser
        time.sleep(3)  # Wait for 3 seconds to see the result
        driver.quit()
        log_message("Browser closed. Test completed.")

print("Profile update test completed. Results have been written to", log_file_path)
