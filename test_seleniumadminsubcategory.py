import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
log_file_path = "test/admin_subcategory_edit_test_results.txt"
with open(log_file_path, "w") as log_file:
    try:
        log_message("Starting the Selenium test...")

        driver.maximize_window()
        log_message("Browser window maximized.")

        # Navigate to the admin login page
        driver.get("http://127.0.0.1:8000/user/login/")
        log_message("Navigated to the login page.")

        # Wait for the email input field to be present
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        log_message("Email input field is visible.")

        # Input the admin email
        email_input.send_keys("cattlecare7@gmail.com")
        log_message("Entered email: cattlecare7@gmail.com")

        # Wait for the password input field to be present
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        log_message("Password input field is visible.")

        # Input the admin password
        password_input.send_keys("cattlecare")
        log_message("Entered password: ******")

        # Wait for the login button to be clickable
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "submit"))
        )
        login_button.click()
        log_message("Clicked the login button.")

        # Wait for the admin dashboard page to load
        WebDriverWait(driver, 10).until(
            EC.title_contains("CattleCare Admin Dashboard")
        )
        log_message("Logged in successfully and navigated to the dashboard.")

        # Now navigate to the subcategory page directly
        driver.get("http://127.0.0.1:8000/user/admin_subcategory/")
        log_message("Navigated directly to the Subcategory page.")

        # Wait for the subcategory page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal"))
        )
        log_message("Subcategory page loaded successfully.")

        # Locate the "Edit" button for the first subcategory and click it
        edit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-target='#editSubcategoryModal1']"))
        )
        edit_button.click()
        log_message("Clicked the edit button for the first subcategory.")

        # Wait for the modal to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "editSubcategoryModal1"))
        )
        log_message("Edit subcategory modal opened.")

        # Find the subcategory name input field and clear the existing value
        subcategory_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "edit_subcategory_name_1"))
        )
        subcategory_name_input.clear()
        log_message("Cleared the existing subcategory name.")

        # Input the new subcategory name: "HR cow"
        subcategory_name_input.send_keys("HR cow")
        log_message("Entered new subcategory name: HR cow")

        # Submit the form
        submit_button = driver.find_element(By.CSS_SELECTOR, "form.editSubcategoryForm button[type='submit']")
        submit_button.click()
        log_message("Submitted the subcategory form.")

        # Wait for the modal to close after submission
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.ID, "editSubcategoryModal1"))
        )
        log_message("Subcategory update reflected on the page.")

        # Check if the success message is displayed
        success_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        if success_message:
            log_message("Success message displayed. Test passed!")
        else:
            log_message("No success message displayed. Test failed!")

    except Exception as e:
        log_message(f"An error occurred: {e}")

    finally:
        # Close the browser
        time.sleep(3)  # Wait for 3 seconds to see the result
        driver.quit()
        log_message("Browser closed. Test completed.")

print("Test completed. Results have been written to", log_file_path)
