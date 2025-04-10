import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestSeleniumRegister:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}
  
    def teardown_method(self, method):
        self.driver.quit()
  
    def test_selenium_register(self):
        self.driver.get("http://127.0.0.1:8000/user/register_page/")
        self.driver.set_window_size(824, 835)

        # Fill in the registration form
        self.driver.find_element(By.NAME, "fname").send_keys("Ashmi")
        self.driver.find_element(By.NAME, "lname").send_keys("Anees")
        self.driver.find_element(By.NAME, "email").send_keys("ashmianees12@gmail.com")
        self.driver.find_element(By.NAME, "password1").send_keys("Ashmi@12")
        self.driver.find_element(By.NAME, "password2").send_keys("Ashmi@12")
        self.driver.find_element(By.NAME, "submit").click()

        # Wait for the login page to load
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.ID, "email"))
        )

        # Fill in the login form
        self.driver.find_element(By.ID, "email").send_keys("ashmianees12@gmail.com")
        self.driver.find_element(By.ID, "password").send_keys("Ashmi@12")
        self.driver.find_element(By.NAME, "submit").click()

        # Wait for the profile completion page to load
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.ID, "house_number"))
        )

        # Fill in the profile completion form
        self.driver.find_element(By.ID, "house_number").send_keys("Keetis House")
        self.driver.find_element(By.ID, "city").send_keys("Kanjirappally")
        self.driver.find_element(By.ID, "phone_number").send_keys("7845965412")
        self.driver.find_element(By.ID, "postal_code").send_keys("686518")

        # Select an image (you may need to adjust the selector based on your HTML structure)
        self.driver.find_element(By.CSS_SELECTOR, ".image-section").click()
        self.driver.find_element(By.CSS_SELECTOR, "button:nth-child(6)").click()

# If running the script directly, use pytest to execute the test
if __name__ == "__main__":
    pytest.main([__file__])
