# Vietnamese Contest Automation Strategy
# Based on analysis of disanketnoi.vn

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ContestAutomator:
    def __init__(self, headless=False, wait_timeout=10):
        """
        Initialize the automation bot
        
        Args:
            headless (bool): Run browser in headless mode
            wait_timeout (int): Maximum wait time for elements
        """
        self.wait_timeout = wait_timeout
        self.driver = None
        self.wait = None
        self.setup_driver(headless)
        self.setup_logging()
    
    def setup_driver(self, headless):
        """Setup Chrome WebDriver with optimal options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Essential options for automation
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, self.wait_timeout)
    
    def setup_logging(self):
        """Setup logging for tracking automation progress"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('contest_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def navigate_to_contest(self):
        """Navigate to the contest page"""
        url = "https://disanketnoi.vn/bai-du-thi/ruoc-gom/"
        self.logger.info(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(2)  # Allow page to load
    
    def find_and_click_login_trigger(self):
        """
        Find the trigger button that reveals Google sign-in popup
        Target: <a class="jet-auth-links__item" href="#elementor-action...">
        """
        try:
            # Specific selector for the login trigger button
            login_trigger_selector = ".jet-auth-links__item"
            
            self.logger.info("Looking for login trigger button...")
            trigger_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, login_trigger_selector))
            )
            
            # Verify it's the correct button by checking the text
            button_text = trigger_btn.text.strip()
            if "Đăng nhập" in button_text:
                self.logger.info(f"Found login trigger button: '{button_text}'")
                trigger_btn.click()
                time.sleep(2)  # Wait for popup to appear
                return True
            else:
                self.logger.warning(f"Found button but text doesn't match: '{button_text}'")
                return False
            
        except TimeoutException:
            self.logger.error("Login trigger button not found - timeout")
            return False
        except Exception as e:
            self.logger.error(f"Error finding login trigger button: {e}")
            return False
    
    def handle_google_login(self, email, password):
        """
        Handle Google OAuth login process
        Target: <a class="mo_btn mo_btn-mo mo_btn-block mo_btn-social mo_btn-google..." onclick="moOpenIdLogin('google','true');">
        
        Args:
            email (str): Google account email
            password (str): Google account password
        """
        try:
            # Wait for the popup to appear and find Google sign-in button
            self.logger.info("Waiting for Google sign-in button to appear...")
            
            # Specific selector for the Google login button
            google_signin_selector = ".mo_btn-google.login-button"
            
            google_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, google_signin_selector))
            )
            
            # Verify it's the correct button
            button_text = google_btn.text.strip()
            if "Login with Google" in button_text or "Google" in button_text:
                self.logger.info(f"Found Google sign-in button: '{button_text}'")
                google_btn.click()
                
                # Handle Google OAuth flow
                return self._complete_google_oauth(email, password)
            else:
                self.logger.warning(f"Found button but text doesn't match: '{button_text}'")
                return False
            
        except TimeoutException:
            self.logger.error("Google sign-in button not found - timeout")
            return False
        except Exception as e:
            self.logger.error(f"Error in Google login: {e}")
            return False
    
    def _complete_google_oauth(self, email, password):
        """Complete the Google OAuth flow"""
        try:
            # Wait for Google login page
            self.wait.until(EC.url_contains("accounts.google.com"))
            
            # Enter email
            email_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "identifierId"))
            )
            email_input.send_keys(email)
            
            # Click Next
            next_btn = self.driver.find_element(By.ID, "identifierNext")
            next_btn.click()
            
            # Enter password
            password_input = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            password_input.send_keys(password)
            
            # Click Sign In
            signin_btn = self.driver.find_element(By.ID, "passwordNext")
            signin_btn.click()
            
            # Wait for redirect back to contest site
            self.wait.until(EC.url_contains("disanketnoi.vn"))
            self.logger.info("Successfully logged in with Google")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in OAuth flow: {e}")
            return False
    
    def click_target_button(self):
        """
        Click the target button after login
        This is the main action you want to perform
        """
        try:
            # Common selectors for vote/action buttons
            target_selectors = [
                ".vote-btn",
                ".submit-btn",
                "button[type='submit']",
                ".elementor-button",
                "input[type='submit']"
            ]
            
            for selector in target_selectors:
                try:
                    target_btn = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    self.logger.info(f"Clicking target button: {selector}")
                    target_btn.click()
                    time.sleep(2)  # Wait for action to complete
                    return True
                except TimeoutException:
                    continue
            
            self.logger.warning("Target button not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error clicking target button: {e}")
            return False
    
    def check_result(self):
        """
        Check if the action was successful
        Returns True if correct value, False otherwise
        """
        try:
            # Look for success indicators
            success_indicators = [
                ".success-message",
                ".alert-success", 
                "[class*='success']",
                "text:contains('thành công')",  # Vietnamese for "successful"
                "text:contains('đã vote')"      # Vietnamese for "voted"
            ]
            
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        self.logger.info("Success confirmed!")
                        return True
                except NoSuchElementException:
                    continue
            
            # Check for error indicators
            error_indicators = [
                ".error-message",
                ".alert-error",
                "[class*='error']"
            ]
            
            for indicator in error_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        self.logger.warning("Error detected")
                        return False
                except NoSuchElementException:
                    continue
            
            self.logger.info("No clear success/error indicator found")
            return True  # Assume success if no error
            
        except Exception as e:
            self.logger.error(f"Error checking result: {e}")
            return False
    
    def logout(self):
        """Logout from current session"""
        try:
            # Look for logout button/link
            logout_selectors = [
                "a[href*='logout']",
                ".logout-btn",
                "button:contains('Đăng xuất')",  # Vietnamese for "Logout"
                ".user-menu .logout"
            ]
            
            for selector in logout_selectors:
                try:
                    logout_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logout_btn.click()
                    time.sleep(2)
                    self.logger.info("Logged out successfully")
                    return True
                except NoSuchElementException:
                    continue
            
            # Alternative: Clear cookies to force logout
            self.driver.delete_all_cookies()
            self.logger.info("Cleared cookies to force logout")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")
            return False
    
    def run_automation_cycle(self, accounts_list, max_cycles=None):
        """
        Run the complete automation cycle
        
        Args:
            accounts_list (list): List of (email, password) tuples
            max_cycles (int): Maximum number of cycles to run
        """
        cycle_count = 0
        successful_actions = 0
        
        try:
            while True:
                if max_cycles and cycle_count >= max_cycles:
                    break
                
                for email, password in accounts_list:
                    cycle_count += 1
                    self.logger.info(f"Starting cycle {cycle_count} with {email}")
                    
                    # Step 1: Navigate to contest
                    self.navigate_to_contest()
                    
                    # Step 2: Find and click login trigger
                    if not self.find_and_click_login_trigger():
                        self.logger.warning("Skipping this cycle - no login trigger")
                        continue
                    
                    # Step 3: Handle Google login
                    if not self.handle_google_login(email, password):
                        self.logger.warning("Login failed - skipping this cycle")
                        continue
                    
                    # Step 4: Click target button
                    if not self.click_target_button():
                        self.logger.warning("Failed to click target button")
                        self.logout()
                        continue
                    
                    # Step 5: Check result
                    if self.check_result():
                        successful_actions += 1
                        self.logger.info(f"Successful action #{successful_actions}")
                    else:
                        self.logger.warning("Action may have failed")
                    
                    # Step 6: Logout
                    self.logout()
                    
                    # Step 7: Wait between cycles
                    time.sleep(5)  # Adjust delay as needed
                    
                    if max_cycles and cycle_count >= max_cycles:
                        break
        
        except KeyboardInterrupt:
            self.logger.info("Automation stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.logger.info(f"Automation completed. Cycles: {cycle_count}, Successful: {successful_actions}")
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    # List of Google accounts (email, password)
    accounts = [
        ("your-email1@gmail.com", "password1"),
        ("your-email2@gmail.com", "password2"),
        # Add more accounts as needed
    ]
    
    # Initialize automator
    bot = ContestAutomator(headless=False)  # Set to True for headless mode
    
    # Run automation
    bot.run_automation_cycle(accounts, max_cycles=10)
