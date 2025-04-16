from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, SessionNotCreatedException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time

class WebAutomator:
    def __init__(self, config, gui):
        self.config = config
        self.gui = gui
        self.driver = None
        self.wait_timeout = 10
        self.page_load_timeout = 30
        self.implicit_wait = 5
    
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-gpu")  # Reduce GPU usage
            chrome_options.add_argument("--disable-extensions")  # Disable extensions
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(self.implicit_wait)
            return True
        except Exception as e:
            self.gui.update_status(f"Driver setup error: {str(e)}")
            return False
    
    def wait_for_element(self, by, selector, timeout=None):
        try:
            timeout = timeout or self.wait_timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except Exception:
            return None

    def safe_click(self, element, retries=3):
        for _ in range(retries):
            try:
                if not element.is_displayed() or not element.is_enabled():
                    time.sleep(0.5)
                    continue
                element.click()
                return True
            except (StaleElementReferenceException, ElementClickInterceptedException):
                time.sleep(0.5)
            except Exception as e:
                self.gui.update_status(f"Click error: {str(e)}")
                return False
        return False

    def find_login_field(self):
        """Try different login field selectors"""
        selectors = [
            (By.NAME, "username"),
            (By.NAME, "email"),
            (By.ID, "username"),
            (By.ID, "email"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.XPATH, "//input[@placeholder='Username' or @placeholder='Email']")
        ]
        
        for by, selector in selectors:
            field = self.wait_for_element(by, selector)
            if field:
                self.gui.update_status(f"Found login field using: {by}={selector}")
                return field
        
        raise TimeoutException("Could not find username/email input field")

    def login(self):
        try:
            self.driver.get(self.config['url'])
            
            # Find and fill login fields with retry
            login_field = self.find_login_field()
            if not login_field:
                return False
                
            password_field = self.wait_for_element(By.NAME, "password")
            if not password_field:
                return False
            
            # Enter credentials
            login_field.clear()
            login_field.send_keys(self.config['username'])
            password_field.clear()
            password_field.send_keys(self.config['password'])
            
            # Find and click login button
            login_button = self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
            if not login_button or not self.safe_click(login_button):
                return False
            
            # Wait for login success
            time.sleep(2)  # Minimum wait for session establishment
            
            # Handle form URL redirect
            if self.config.get('form_url'):
                self.gui.update_status("Redirecting to form page...")
                try:
                    self.driver.get(self.config['form_url'])
                    if not self.wait_for_page_load():
                        return False
                except Exception as e:
                    self.gui.update_status(f"Redirect error: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            self.gui.update_status(f"Login error: {str(e)}")
            return False

    def wait_for_page_load(self, timeout=None):
        timeout = timeout or self.page_load_timeout
        try:
            # Wait for document ready state
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            # Wait for jQuery if present
            jquery_ready = """
            return (typeof jQuery !== 'undefined') ? 
                   jQuery.active == 0 : true
            """
            WebDriverWait(self.driver, 5).until(
                lambda driver: driver.execute_script(jquery_ready)
            )
            return True
        except Exception:
            return False

    def get_by_type(self, selector_type):
        selector_map = {
            "CSS": By.CSS_SELECTOR,
            "ID": By.ID,
            "XPATH": By.XPATH
        }
        return selector_map.get(selector_type, By.CSS_SELECTOR)
    
    def perform_action(self, action):
        try:
            selector_type = self.get_by_type(action['selector_type'])
            element = self.wait_for_element(selector_type, action['selector'])
            
            if not element:
                return False
            
            if action['action'] == 'click':
                return self.safe_click(element)
            elif action['action'] == 'input':
                element.clear()
                element.send_keys(action.get('value', ''))
            elif action['action'] == 'wait':
                # Just wait for element presence
                pass
                
            time.sleep(float(action['delay']))
            return True
            
        except Exception as e:
            self.gui.update_status(f"Action failed: {str(e)}")
            return False

    def fill_form(self, data_row):
        try:
            if not self.wait_for_page_load():
                return False
                
            # Fill form fields with improved error handling
            for mapping in self.config['field_mappings']:
                selector_type = self.get_by_type(mapping['selector_type'])
                element = self.wait_for_element(selector_type, mapping['web_selector'])
                if not element:
                    continue
                
                try:
                    element.clear()
                    element.send_keys(str(data_row[mapping['excel_column']]))
                except Exception as e:
                    self.gui.update_status(f"Field fill error: {str(e)}")
                    continue
                
                time.sleep(0.2)  # Reduced delay between fields
            
            # Execute post-submit actions
            return self.execute_post_submit_actions()
            
        except Exception as e:
            self.gui.update_status(f"Form fill error: {str(e)}")
            return False

    def execute_post_submit_actions(self):
        for action in sorted(self.config['post_submit_actions'], key=lambda x: x['order']):
            if not self.perform_action(action):
                return False
            if not self.wait_for_page_load(5):  # Short timeout for action completion
                self.gui.update_status("Page load timeout after action")
        return True

    def run_automation(self, data):
        if not self.setup_driver():
            self.gui.update_status("Failed to initialize Chrome")
            return
        
        total_rows = len(data)
        
        if not self.login():
            self.gui.update_status("Login failed")
            self.driver.quit()
            return
        
        self.gui.update_status("Login successful")
        self.gui.progress['maximum'] = total_rows
        
        for index, row in data.iterrows():
            if self.gui.stop_flag:
                self.gui.update_status("Automation stopped by user")
                break
                
            while self.gui.paused:
                time.sleep(0.5)  # Wait while paused
                continue
                
            self.gui.progress['value'] = index + 1
            self.gui.update_status(f"Processing row {index + 1} of {total_rows}")
            
            if not self.fill_form(row):
                self.gui.update_status(f"Error in row {index + 1}")
                continue
            self.gui.update_status(f"Successfully processed row {index + 1}")
        
        self.gui.update_status("Automation completed")
        self.driver.quit()
