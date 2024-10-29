import logging
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging for monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
URL = 'https://accounts.google.com/signup'
FIRST_NAMES_FILE = 'firstNames.txt'
LAST_NAMES_FILE = 'lastNames.txt'
CREDENTIALS_LOG_FILE = 'account_credentials.txt'  # File to save credentials

# Helper functions for random data generation
def load_names(file_path):
    """Load names from a text file into a list."""
    try:
        with open(file_path, 'r') as file:
            names = file.read().splitlines()
        logging.info(f"Loaded {len(names)} names from {file_path}")
        return names
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return []

def generate_random_name(first_names, last_names):
    """Select a random first and last name from lists."""
    return random.choice(first_names), random.choice(last_names)

def generate_random_username():
    """Generate a random username with a random number suffix."""
    name_part = ''.join(random.choices(string.ascii_lowercase, k=5))
    number_part = random.randint(1000, 9999)
    return f"{name_part}{number_part}"

def generate_random_password():
    """Generate a secure random password."""
    letters = string.ascii_letters
    digits = string.digits
    special_chars = "!@#$%^&*"
    all_chars = letters + digits + special_chars
    password = ''.join(random.choices(all_chars, k=10))
    return password

def log_credentials(first_name, last_name, username, password):
    """Log the generated credentials to a file with a timestamp."""
    with open(CREDENTIALS_LOG_FILE, 'a') as file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - Name: {first_name} {last_name}, Username: {username}, Password: {password}\n")
    logging.info("Credentials saved to file.")

class GoogleAccountCreator:
    def __init__(self, first_names, last_names):
        # Use WebDriverManager to handle the ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 20)  # Increased wait time to 20 seconds
        self.first_names = first_names
        self.last_names = last_names

    def open_signup_page(self):
        """Open the Google Sign-Up page."""
        logging.info("Navigating to Google sign-up page.")
        self.driver.get(URL)
        time.sleep(random.randint(7, 12))  # Random delay between 7 and 12 seconds

    def find_next_button(self):
        """Attempt multiple locators to find the 'Next' button."""
        next_button_locators = [
            # Common ID-based and text-based XPaths
            (By.XPATH, '//*[@id="accountDetailsNext"]'),
            (By.XPATH, '//button[contains(text(), "Next")]'),
            (By.XPATH, '//button[contains(text(), "Next step")]'),
            (By.XPATH, '//button[contains(text(), "Continue")]'),
            
            # Locators using aria-label and role attributes
            (By.XPATH, '//div[@role="button" and @aria-label="Next"]'),
            (By.XPATH, '//div[@role="button" and contains(@aria-label, "Next")]'),
            
            # Class-based locators (use partial matches to cover changes in class names)
            (By.XPATH, '//div[contains(@class, "VfPpkd-RLmnJb") and @role="button"]'),
            (By.XPATH, '//button[contains(@class, "VfPpkd-LgbsSe")]'),  # Common class for Google buttons
            
            # CSS Selectors for buttons with common attributes
            (By.CSS_SELECTOR, 'button[aria-label="Next"]'),
            (By.CSS_SELECTOR, 'div[role="button"][aria-label="Next"]'),
            (By.CSS_SELECTOR, '.VfPpkd-RLmnJb[role="button"]'),
            
            # XPath relative to the last name field (useful if the button follows a known field)
            (By.XPATH, '//*[@id="lastName"]/following::div[@role="button"]')
        ]
        
        for by, locator in next_button_locators:
            try:
                button = self.wait.until(EC.element_to_be_clickable((by, locator)))
                logging.info(f"'Next' button found using locator: {locator}")
                return button
            except TimeoutException:
                logging.warning(f"'Next' button not found using locator: {locator}")
        
        # If none of the locators worked, raise an exception
        raise NoSuchElementException("Could not locate the 'Next' button with any provided locators.")

    def fill_form(self, first_name: str, last_name: str, username: str, password: str):
        """Fill out the sign-up form using XPath selectors."""
        try:
            logging.info("Filling out the sign-up form.")
            
            # Fill in the first name using XPath
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="firstName"]'))).send_keys(first_name)
            
            # Fill in the last name using XPath
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lastName"]'))).send_keys(last_name)
            
            # Find and click the "Next" button
            next_button = self.find_next_button()
            next_button.click()

            # Fill in the username using XPath
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="username"]'))).send_keys(username)
            
            # Fill in the password using XPath
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@name="Passwd"]'))).send_keys(password)
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@name="ConfirmPasswd"]'))).send_keys(password)
        except NoSuchElementException as e:
            logging.error(f"An element was not found: {e}")
        except TimeoutException:
            logging.error("Loading the form took too long.")

    def submit_form(self):
        """Submit the form by pressing the Return key in the last field using XPath."""
        try:
            logging.info("Submitting the form by pressing Enter.")
            
            # Locate the last filled input field (e.g., ConfirmPasswd) and press Enter
            confirm_password_field = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@name="ConfirmPasswd"]'))
            )
            confirm_password_field.send_keys(Keys.RETURN)
            
        except TimeoutException:
            logging.error("Could not locate the last field in time.")
            raise Exception("Form submission failed due to TimeoutException.")
        except Exception as e:
            logging.error(f"An unexpected error occurred during form submission: {e}")
            raise e  # Re-raise the exception to ensure it propagates to the create_account method

    def close_browser(self):
        """Close the browser."""
        logging.info("Closing the browser.")
        self.driver.quit()

    def create_account(self):
        """Complete the full account creation process with random data and log credentials only if successful."""
        first_name, last_name = generate_random_name(self.first_names, self.last_names)
        username = generate_random_username()
        password = generate_random_password()
        
        logging.info(f"Creating account for: {first_name} {last_name}, Username: {username}")
        
        submission_successful = False  # Flag to track successful submission

        try:
            self.open_signup_page()
            self.fill_form(first_name, last_name, username, password)
            self.submit_form()
            
            # Mark as successful if all steps complete without error
            submission_successful = True
            
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        finally:
            # Log credentials only if submission was successful
            if submission_successful:
                log_credentials(first_name, last_name, username, password)
            
            # Ensure the browser closes even if an error occurs
            time.sleep(random.randint(7, 12))  # Optional random delay before closing
            self.close_browser()

# Run the script
if __name__ == "__main__":
    # Load names from text files
    first_names = load_names(FIRST_NAMES_FILE)
    last_names = load_names(LAST_NAMES_FILE)
    
    if not first_names or not last_names:
        logging.error("First or last names list is empty. Ensure text files are correctly populated.")
    else:
        account_creator = GoogleAccountCreator(first_names, last_names)
        account_creator.create_account()
