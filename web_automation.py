from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, SessionNotCreatedException, StaleElementReferenceException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time

class WebAutomator:
    def __init__(self, config, gui):
        self.config = config
        self.gui = gui
        self.driver = None
        # Use settings from GUI
        settings = gui.settings_manager.settings
        self.wait_timeout = settings['wait_timeout']
        self.page_load_timeout = settings['page_load_timeout']
        self.implicit_wait = settings['implicit_wait']
        self.max_retries = settings['max_retries']
        self.action_delay = settings['action_delay']
    
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-gpu")  # Reduce GPU usage
            chrome_options.add_argument("--disable-extensions")  # Disable extensions
            chrome_options.add_argument("--disable-dev-shm-usage")  # Add for stability
            chrome_options.add_argument("--no-sandbox")  # Add for stability
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(self.implicit_wait)
            return True
        except Exception as e:
            self.gui.update_status(f"Driver setup error: {str(e)}")
            return False
    
    def wait_for_element(self, by, selector, timeout=None, check_visible=True):
        """Enhanced wait with visibility check and better error handling"""
        try:
            timeout = timeout or self.wait_timeout
            if check_visible:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, selector))
                )
            else:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
            return element
        except TimeoutException:
            return None
        except Exception as e:
            self.gui.update_status(f"Wait error: {str(e)}")
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

    def verify_login_success(self):
        """Verify that login was successful"""
        try:
            # Wait for login page URL to change
            current_url = self.driver.current_url
            if current_url == self.config['url']:
                # Still on login page, check for error messages
                error_selectors = [
                    (By.CLASS_NAME, "alert-danger"),
                    (By.CLASS_NAME, "error-message"),
                    (By.CSS_SELECTOR, ".error"),
                    (By.XPATH, "//div[contains(text(), 'Invalid')]")
                ]
                for by, selector in error_selectors:
                    error = self.wait_for_element(by, selector, timeout=1, check_visible=True)
                    if error:
                        self.gui.update_status(f"Login failed: {error.text}")
                        return False
                return False
            return True
        except Exception as e:
            self.gui.update_status(f"Login verification error: {str(e)}")
            return False

    def login(self):
        try:
            self.driver.get(self.config['url'])
            self.wait_for_page_load()
            
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
            
            # Wait for login success and verify
            time.sleep(2)  # Short wait for initial page transition
            self.close_dialogs()
            
            # Check login success with retry
            for attempt in range(3):
                if self.verify_login_success():
                    break
                time.sleep(1)
                if attempt == 2:  # Last attempt failed
                    self.gui.update_status("Login verification failed - still on login page")
                    return False
            
            # Handle form URL redirect if specified
            if self.config.get('form_url'):
                return self.redirect_to_form()
            
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
    
    def check_skip_condition(self, condition, selector_type, selector):
        """Check if skip condition is met"""
        try:
            by_type = self.get_by_type(selector_type)
            if condition == "exists":
                element = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((by_type, selector))
                )
                return True
            elif condition == "not_exists":
                try:
                    self.driver.find_element(by_type, selector)
                    return False
                except NoSuchElementException:
                    return True
            elif condition.startswith("contains:"):
                text = condition.split(":", 1)[1]
                element = self.driver.find_element(by_type, selector)
                return text in element.text
            return False
        except (TimeoutException, NoSuchElementException):
            return False if condition == "exists" else True

    def handle_action(self, action, retry_count=0):
        """Add retry logic for failed actions"""
        try:
            result = self._execute_action(action)
            if not result and retry_count < self.max_retries:
                self.gui.update_status(f"Retrying action {retry_count + 1}/{self.max_retries}")
                time.sleep(1)  # Wait before retry
                return self.handle_action(action, retry_count + 1)
            return result
        except Exception as e:
            self.gui.update_status(f"Action error: {str(e)}")
            return False

    def _execute_action(self, action):
        """Separated action execution logic"""
        by_type = self.get_by_type(action["selector_type"])
        try:
            element = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((by_type, action["selector"]))
            )
            
            if action["action"] == "click":
                element.click()
            elif action["action"] == "input":
                element.clear()
                element.send_keys(action["value"])
            elif action["action"] == "wait":
                # Already waited for element
                pass
            elif action["action"] == "confirm":
                if self.config.get("auto_confirm"):
                    alert = self.driver.switch_to.alert
                    alert.accept()
            
            if float(action["delay"]) > 0:
                self.driver.implicitly_wait(float(action["delay"]))
                
        except TimeoutException:
            self.gui.update_status(f"Timeout waiting for element: {action['selector']}")
            return False
        return True

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

    def close_dialogs(self, max_attempts=3):
        """Close any open dialogs/alerts"""
        try:
            for _ in range(max_attempts):
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    time.sleep(0.5)
                except:
                    break
        except Exception as e:
            self.gui.update_status(f"Dialog close error: {str(e)}")

    def redirect_to_form(self):
        """Redirect back to form URL"""
        try:
            if self.config.get('form_url'):
                self.gui.update_status("Redirecting to form page...")
                self.driver.get(self.config['form_url'])
                return self.wait_for_page_load()
            return True
        except Exception as e:
            self.gui.update_status(f"Redirect error: {str(e)}")
            return False

    def execute_post_submit_actions(self):
        for action in sorted(self.config['post_submit_actions'], key=lambda x: x['order']):
            if action["action"] == "skip":
                should_skip = self.handle_action(action)
                if should_skip:
                    self.gui.update_status("Skipping row due to condition met")
                    self.close_dialogs()  # Close any dialogs
                    if not self.redirect_to_form():  # Redirect back to form
                        self.gui.update_status("Failed to redirect after skip")
                    return True
            else:
                if not self.handle_action(action):
                    return False
                if not self.wait_for_page_load(5):
                    self.gui.update_status("Page load timeout after action")
        return True

    def run_automation(self, data):
        if not self.setup_driver():
            self.gui.update_status("Failed to initialize Chrome")
            return
            
        try:
            if data is None or data.empty:
                raise ValueError("No data loaded from Excel file")
                
            total_rows = len(data)
            if total_rows == 0:
                raise ValueError("Excel file contains no data rows")
            
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
        
        except Exception as e:
            self.gui.update_status(f"Automation error: {str(e)}")
        finally:
            self.gui.update_status("Automation completed")
            if self.driver:
                self.driver.quit()
