# Contest Voting Automation Script
# Automatically votes with multiple Google accounts on Vietnamese contest website

import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as EdgeOptions

class ContestVotingBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.browser_choice = None
        self.browser_path = None
        self.profile_path = None
        self.voted_accounts_file = "voted_accounts.txt"  # File to store voted accounts
        self.unusable_accounts_file = "unusable_accounts.txt"  # File to store unusable accounts
        self.voted_accounts = set()  # Track accounts that have already voted
        self.unusable_accounts = set()  # Track accounts that require password/unusable
        self.successful_votes = 0    # Track successful votes
        self.load_voted_accounts()   # Load previously voted accounts from file
        self.load_unusable_accounts()  # Load previously unusable accounts from file
        self.select_browser()
        self.setup_driver()
    
    def get_browser_locations(self):
        """Get default browser locations for Windows"""
        username = os.getenv('USERNAME')
        
        browsers = {
            "chrome": {
                "name": "Google Chrome",
                "executable_paths": [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    rf"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe"
                ],
                "profile_paths": [
                    rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data",
                    rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Default"
                ]
            },
            "brave": {
                "name": "Brave Browser",
                "executable_paths": [
                    rf"C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe",
                    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
                ],
                "profile_paths": [
                    rf"C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\User Data",
                    rf"C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default"
                ]
            },
            "edge": {
                "name": "Microsoft Edge",
                "executable_paths": [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    rf"C:\Users\{username}\AppData\Local\Microsoft\Edge\Application\msedge.exe"
                ],
                "profile_paths": [
                    rf"C:\Users\{username}\AppData\Local\Microsoft\Edge\User Data",
                    rf"C:\Users\{username}\AppData\Local\Microsoft\Edge\User Data\Default"
                ]
            },
            "firefox": {
                "name": "Mozilla Firefox",
                "executable_paths": [
                    r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                    rf"C:\Users\{username}\AppData\Local\Mozilla Firefox\firefox.exe"
                ],
                "profile_paths": [
                    rf"C:\Users\{username}\AppData\Roaming\Mozilla\Firefox\Profiles",
                    rf"C:\Users\{username}\AppData\Local\Mozilla\Firefox\Profiles"
                ]
            },
            "opera": {
                "name": "Opera Browser",
                "executable_paths": [
                    rf"C:\Users\{username}\AppData\Local\Programs\Opera\opera.exe",
                    r"C:\Program Files\Opera\opera.exe",
                    r"C:\Program Files (x86)\Opera\opera.exe"
                ],
                "profile_paths": [
                    rf"C:\Users\{username}\AppData\Roaming\Opera Software\Opera Stable",
                    rf"C:\Users\{username}\AppData\Local\Opera Software\Opera Stable"
                ]
            }
        }
        
        return browsers
    
    def find_browser_executable(self, browser_key):
        """Find the executable path for a specific browser"""
        browsers = self.get_browser_locations()
        if browser_key not in browsers:
            return None, None
        
        browser_info = browsers[browser_key]
        
        # Find executable
        executable_path = None
        for path in browser_info["executable_paths"]:
            if os.path.exists(path):
                executable_path = path
                break
        
        # Find profile
        profile_path = None
        for path in browser_info["profile_paths"]:
            if os.path.exists(path):
                profile_path = path
                break
        
        return executable_path, profile_path
    
    def detect_chrome_profiles(self, user_data_dir):
        """
        Detect available Chrome profiles in the user data directory
        
        Args:
            user_data_dir (str): Path to Chrome User Data directory
            
        Returns:
            list: List of available profile directories
        """
        if not os.path.exists(user_data_dir):
            return []
        
        profiles = []
        
        # Check for Default profile
        default_path = os.path.join(user_data_dir, "Default")
        if os.path.exists(default_path):
            profiles.append("Default")
        
        # Check for numbered profiles (Profile 1, Profile 2, etc.)
        for i in range(1, 20):  # Check up to Profile 19
            profile_name = f"Profile {i}"
            profile_path = os.path.join(user_data_dir, profile_name)
            if os.path.exists(profile_path):
                profiles.append(profile_name)
        
        return profiles
    
    def select_chrome_profile(self, user_data_dir):
        """
        Let user select Chrome profile if multiple profiles exist
        
        Args:
            user_data_dir (str): Path to Chrome User Data directory
            
        Returns:
            str: Full path to selected profile directory
        """
        profiles = self.detect_chrome_profiles(user_data_dir)
        
        if not profiles:
            print("No Chrome profiles found!")
            default_path = os.path.join(user_data_dir, "Default")
            print(f"Using default path: {default_path}")
            return default_path
        
        if len(profiles) == 1:
            profile_path = os.path.join(user_data_dir, profiles[0])
            print(f"Using Chrome profile: {profiles[0]}")
            print(f"Profile directory: {profile_path}")
            return profile_path
        
        # Multiple profiles found - let user choose
        print("\nMultiple Chrome profiles detected:")
        print("=" * 40)
        for i, profile in enumerate(profiles):
            profile_path = os.path.join(user_data_dir, profile)
            print(f"{i + 1}. {profile}")
            print(f"   Directory: {profile_path}")
        print()
        
        while True:
            try:
                choice = input(f"Select profile (1-{len(profiles)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(profiles):
                    selected_profile = profiles[choice_idx]
                    selected_path = os.path.join(user_data_dir, selected_profile)
                    print(f"Selected Chrome profile: {selected_profile}")
                    print(f"Using directory: {selected_path}")
                    return selected_path
                else:
                    print(f"Please enter a number between 1 and {len(profiles)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nUsing Default profile")
                default_path = os.path.join(user_data_dir, "Default")
                return default_path
    
    def select_browser(self):
        """Let user select which browser to use"""
        browsers = self.get_browser_locations()
        
        print("Available Browsers:")
        print("=" * 50)
        
        available_browsers = []
        for key, info in browsers.items():
            executable_path, profile_path = self.find_browser_executable(key)
            status = "Available" if executable_path else "Not Found"
            print(f"{len(available_browsers) + 1}. {info['name']} - {status}")
            if executable_path:
                print(f"   Executable: {executable_path}")
                print(f"   Profile: {profile_path}")
                available_browsers.append((key, executable_path, profile_path))
            print()
        
        if not available_browsers:
            print("No supported browsers found!")
            exit(1)
        
        # Let user choose
        while True:
            try:
                choice = input(f"Select browser (1-{len(available_browsers)}): ").strip()
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(available_browsers):
                    self.browser_choice, self.browser_path, self.profile_path = available_browsers[choice_idx]
                    browser_name = browsers[self.browser_choice]["name"]
                    print(f"Selected: {browser_name}")
                    print(f"Using: {self.browser_path}")
                    if self.profile_path:
                        print(f"Profile: {self.profile_path}")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter a number.")
    
    def setup_driver(self):
        """Setup WebDriver based on selected browser"""
        if self.browser_choice in ["chrome", "brave", "edge", "opera"]:
            self.setup_chromium_driver()
        elif self.browser_choice == "firefox":
            self.setup_firefox_driver()
        else:
            raise ValueError(f"Unsupported browser: {self.browser_choice}")
    
    def setup_chromium_driver(self):
        """Setup Chromium-based browsers (Chrome, Brave, Edge, Opera)"""
        chrome_options = Options()
        
        # Set browser executable path
        chrome_options.binary_location = self.browser_path
        
        # Handle profile selection differently for Chrome vs other browsers
        if self.profile_path:
            if self.browser_choice == "chrome":
                # For Chrome, let user select specific profile directory
                selected_profile_path = self.select_chrome_profile(self.profile_path)
                
                # Use the specific profile directory directly
                chrome_options.add_argument(f"--user-data-dir={selected_profile_path}")
                print(f"Using Chrome profile directory: {selected_profile_path}")
                print("Note: Chrome will use this profile directly (no copying)")
            else:
                # For other Chromium browsers, use default behavior
                chrome_options.add_argument(f"--user-data-dir={self.profile_path}")
                chrome_options.add_argument("--profile-directory=Default")
                print("Using saved profile - your logged-in accounts will be available!")
        else:
            print("No profile found - using clean session")
        
        # Essential options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--remote-debugging-port=9222")  # Add remote debugging port
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # SSL and security options to reduce errors
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--log-level=3")  # Suppress INFO, WARNING, ERROR
        
        # Keep browser open after script ends
        chrome_options.add_experimental_option("detach", True)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            
            # Hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"{self.get_browser_locations()[self.browser_choice]['name']} initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing {self.browser_choice}: {e}")
            print("Make sure to close all browser windows first")
            raise
    
    def setup_firefox_driver(self):
        """Setup Firefox WebDriver"""
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        
        firefox_options = FirefoxOptions()
        firefox_options.binary_location = self.browser_path
        
        # Automatically use profile if available
        if self.profile_path:
            print("Using saved Firefox profile")
            # Firefox profile setup is more complex
        else:
            print("No Firefox profile found - using clean session")
        
        try:
            self.driver = webdriver.Firefox(options=firefox_options)
            self.wait = WebDriverWait(self.driver, 15)
            print("Firefox initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing Firefox: {e}")
            print("Make sure geckodriver is installed: pip install selenium[firefox]")
            raise
    
    def load_voted_accounts(self):
        """
        Load previously voted accounts from file
        """
        try:
            if os.path.exists(self.voted_accounts_file):
                with open(self.voted_accounts_file, 'r', encoding='utf-8') as f:
                    accounts = [line.strip() for line in f.readlines() if line.strip()]
                    self.voted_accounts = set(accounts)
                print(f"Loaded {len(self.voted_accounts)} previously voted accounts from {self.voted_accounts_file}")
                if self.voted_accounts:
                    print(f"Previously voted accounts: {', '.join(list(self.voted_accounts)[:3])}{'...' if len(self.voted_accounts) > 3 else ''}")
            else:
                print(f"No previous voted accounts file found - starting fresh")
                self.voted_accounts = set()
        except Exception as e:
            print(f"Error loading voted accounts: {e}")
            self.voted_accounts = set()
    
    def save_voted_accounts(self):
        """
        Save voted accounts to file for persistence across runs
        """
        try:
            with open(self.voted_accounts_file, 'w', encoding='utf-8') as f:
                for account in sorted(self.voted_accounts):
                    f.write(f"{account}\n")
            print(f"Saved {len(self.voted_accounts)} voted accounts to {self.voted_accounts_file}")
        except Exception as e:
            print(f"Error saving voted accounts: {e}")
    
    def load_unusable_accounts(self):
        """
        Load previously unusable accounts from file
        """
        try:
            if os.path.exists(self.unusable_accounts_file):
                with open(self.unusable_accounts_file, 'r', encoding='utf-8') as f:
                    accounts = [line.strip() for line in f.readlines() if line.strip()]
                    self.unusable_accounts = set(accounts)
                print(f"Loaded {len(self.unusable_accounts)} previously unusable accounts from {self.unusable_accounts_file}")
                if self.unusable_accounts:
                    print(f"Unusable accounts: {', '.join(list(self.unusable_accounts)[:3])}{'...' if len(self.unusable_accounts) > 3 else ''}")
            else:
                print(f"No previous unusable accounts file found")
                self.unusable_accounts = set()
        except Exception as e:
            print(f"Error loading unusable accounts: {e}")
            self.unusable_accounts = set()
    
    def save_unusable_accounts(self):
        """
        Save unusable accounts to file for persistence across runs
        """
        try:
            with open(self.unusable_accounts_file, 'w', encoding='utf-8') as f:
                for account in sorted(self.unusable_accounts):
                    f.write(f"{account}\n")
            print(f"Saved {len(self.unusable_accounts)} unusable accounts to {self.unusable_accounts_file}")
        except Exception as e:
            print(f"Error saving unusable accounts: {e}")
    
    def add_unusable_account(self, email):
        """
        Add an account to the unusable list and save to file
        
        Args:
            email (str): Email address of the account that requires password/verification
        """
        if email and email not in self.unusable_accounts:
            self.unusable_accounts.add(email)
            self.save_unusable_accounts()
            print(f"Added {email} to unusable accounts list (requires password/verification)")
        elif email in self.unusable_accounts:
            print(f"{email} already in unusable accounts list")

    def add_voted_account(self, email):
        """
        Add an account to the voted list and save to file
        
        Args:
            email (str): Email address of the account that voted
        """
        if email and email not in self.voted_accounts:
            self.voted_accounts.add(email)
            self.save_voted_accounts()
            print(f"Added {email} to voted accounts list")
        elif email in self.voted_accounts:
            print(f"{email} already in voted accounts list")

    def select_google_account_automatically(self, start_from_index=0):
        """
        Automatically select Google account from the list, starting from specified index
        
        Args:
            start_from_index (int): Which account index to start from (0-based)
        
        Returns:
            tuple: (success, account_email, account_index) or (False, None, None) if failed
        """
        try:
            print(f"Looking for Google account selection list...")
            
            # Wait for the account selection list to appear
            account_list = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.Dl08I"))
            )
            
            # Find all account items (excluding the "Use another account" option)
            account_items = account_list.find_elements(
                By.CSS_SELECTOR, 
                'li.aZvCDf:not(.B682ne) div.VV3oRb[data-authuser][data-identifier]'
            )
            
            if not account_items:
                print("No Google accounts found in the list")
                return False, None, None
            
            print(f"Found {len(account_items)} Google accounts available")
            
            # List all accounts for reference
            available_accounts = []
            for i, item in enumerate(account_items):
                email = item.get_attribute('data-identifier')
                authuser = item.get_attribute('data-authuser')
                
                # Determine account status
                if email in self.voted_accounts:
                    status = "Already voted"
                elif email in self.unusable_accounts:
                    status = "Unusable (password/verification required)"
                else:
                    status = "Available"
                
                print(f"   {i}: {email} (authuser={authuser}) - {status}")
                
                # Only add accounts that are not voted and not unusable
                if email not in self.voted_accounts and email not in self.unusable_accounts:
                    available_accounts.append((i, item, email, authuser))
            
            if not available_accounts:
                print("All accounts have already been voted or are unusable!")
                return False, None, None
            
            # Select the first available account (not voted yet)
            for account_index, account_item, email, authuser in available_accounts:
                if account_index < start_from_index:
                    continue
                    
                print(f"Attempting to select account {account_index}: {email}")
                
                # Click the account
                account_item.click()
                time.sleep(3)  # Wait for selection to process
                
                # Handle potential authorization prompt
                if "accounts.google.com" in self.driver.current_url:
                    print(f"Handling authorization for {email}...")
                    
                    # Check for password requirement or verification prompt first
                    try:
                        page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                        password_indicators = [
                            "enter password", "nhập mật khẩu của bạn", "nhập mật khẩu",
                            "enter your password", "type your password",
                            "xác minh danh tính của bạn", "verify it's you",
                            "to help keep your account safe, google wants to make sure it's really you"
                        ]
                        
                        requires_password = any(indicator in page_text for indicator in password_indicators)
                        
                        if requires_password:
                            print(f"Password/verification required for {email} - marking as unusable and trying next account")
                            self.add_unusable_account(email)
                            # Go back to account selection and continue with next account
                            try:
                                self.driver.back()
                                time.sleep(3)  # Give more time for page to load
                                
                                # Wait for account list to be available again
                                self.wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.Dl08I"))
                                )
                                print("Returned to account selection page, continuing with next account...")
                                continue  # Continue to next account in the loop
                            except Exception as back_error:
                                print(f"Error going back to account selection: {back_error}")
                                # If we can't go back, return False to retry the whole process
                                return False, None, None
                    except Exception as e:
                        print(f"Error checking for password prompt: {e}")
                    
                    auth_success = self.handle_google_authorization()
                    if not auth_success:
                        print(f"Authorization failed for {email}")
                        continue
                    time.sleep(3)  # Wait after authorization
                
                # Check if we were redirected back to the contest site
                current_url = self.driver.current_url
                if "disanketnoi.vn" in current_url:
                    print(f"Successfully selected account: {email}")
                    
                    # Redirect to target page if not already there
                    target_url = "https://disanketnoi.vn/bai-du-thi/ruoc-gom/"
                    redirect_success = self.redirect_to_target_page(target_url)
                    
                    return True, email, account_index
                elif "accounts.google.com" in current_url:
                    print(f"Account {email} requires additional authentication")
                    # Could be 2FA or other verification - skip for now
                    continue
                else:
                    print(f"Unexpected redirect for {email}: {current_url}")
                    time.sleep(2)
                    continue
            
            print("No available accounts could be selected automatically")
            return False, None, None
            
        except Exception as e:
            print(f"Error selecting Google account: {e}")
            return False, None, None
    
    def check_if_account_already_voted(self):
        """
        Check if the current account has already voted by examining the vote button state
        
        Returns:
            bool: True if already voted, False if can still vote
        """
        try:
            # Look for the specific vote button indicators
            vote_button_selector = ".jet-data-store-link.jet-add-to-store"
            
            # Wait a moment for page to load
            time.sleep(2)
            
            # Find vote buttons
            vote_buttons = self.driver.find_elements(By.CSS_SELECTOR, vote_button_selector)
            
            if not vote_buttons:
                print("No vote buttons found - page may not be loaded properly")
                return False
            
            for button in vote_buttons:
                if button.is_displayed():
                    # Check button classes and content
                    button_classes = button.get_attribute('class')
                    button_text = button.text.strip()
                    
                    # Check if button indicates already voted
                    if 'in-store' in button_classes:
                        print(f"Account already voted - button shows: '{button_text}'")
                        return True
                    elif 'Đã bình chọn' in button_text:
                        print(f"Account already voted - text shows: '{button_text}'")
                        return True
                    elif 'Bình chọn' in button_text and 'in-store' not in button_classes:
                        print(f"Account can vote - button shows: '{button_text}'")
                        return False
            
            print("Account appears to be available for voting")
            return False
            
        except Exception as e:
            print(f"Error checking vote status: {e}")
            return False  # Assume can vote if check fails
    
    def click_vote_button(self):
        """
        Click the vote button for the current account
        
        Returns:
            bool: True if vote was successful, False otherwise
        """
        try:
            print("Looking for vote button...")
            
            # Look for the voteable button (not already voted)
            vote_button_selector = ".jet-data-store-link.jet-add-to-store:not(.in-store)"
            
            vote_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, vote_button_selector))
            )
            
            button_text = vote_button.text.strip()
            print(f"Found vote button: '{button_text}'")
            
            if 'Bình chọn' in button_text:
                print("Clicking vote button...")
                vote_button.click()
                time.sleep(3)  # Wait for vote to process
                
                # Verify vote was successful by checking if button changed
                time.sleep(2)
                updated_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".jet-data-store-link")
                for button in updated_buttons:
                    if button.is_displayed() and 'Đã bình chọn' in button.text:
                        print("Vote successful! Button changed to 'Đã bình chọn'")
                        return True
                
                print("Vote may have failed - button state unclear")
                return False
            else:
                print(f"Button text doesn't match expected 'Bình chọn': '{button_text}'")
                return False
                
        except Exception as e:
            print(f"Error clicking vote button: {e}")
            return False
    
    def handle_google_authorization(self):
        """
        Handle Google authorization by only clicking continue/proceed buttons
        Avoids cancel/back buttons to prevent authorization failures
        
        Returns:
            bool: True if authorization handled or not needed, False if failed
        """
        try:
            print("Checking for Google authorization prompt...")
            
            # Wait briefly to see if authorization screen appears
            time.sleep(3)
            
            # Define allowed proceed/continue button texts (case-insensitive)
            allowed_button_texts = [
                'continue', 'next', 'allow', 'proceed', 'accept', 'authorize', 'confirm',
                'tiếp tục', 'cho phép', 'đồng ý', 'xác nhận', 'chấp nhận'
            ]
            
            # Define blacklisted cancel/back button texts (case-insensitive)
            blacklisted_button_texts = [
                'cancel', 'back', 'return', 'deny', 'refuse', 'decline', 'reject',
                'hủy', 'hủy bỏ', 'trở lại', 'quay lại', 'từ chối', 'không', 'thoát'
            ]
            
            # Find all clickable buttons on the page
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            all_buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, "[role='button']"))
            all_buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, "input[type='button']"))
            all_buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']"))
            
            print(f"Found {len(all_buttons)} potential buttons on page")
            
            for button in all_buttons:
                try:
                    if not button.is_displayed() or not button.is_enabled():
                        continue
                    
                    # Get button text from various sources
                    button_text = ""
                    if button.text:
                        button_text = button.text.strip().lower()
                    elif button.get_attribute("value"):
                        button_text = button.get_attribute("value").strip().lower()
                    elif button.get_attribute("aria-label"):
                        button_text = button.get_attribute("aria-label").strip().lower()
                    
                    # Also check for text in child elements
                    if not button_text:
                        try:
                            spans = button.find_elements(By.TAG_NAME, "span")
                            for span in spans:
                                if span.text:
                                    button_text = span.text.strip().lower()
                                    break
                        except:
                            pass
                    
                    if not button_text:
                        continue
                    
                    print(f"Checking button with text: '{button_text}'")
                    
                    # Check if button text is blacklisted (cancel/back buttons)
                    is_blacklisted = any(blacklisted_text in button_text for blacklisted_text in blacklisted_button_texts)
                    if is_blacklisted:
                        print(f"Skipping blacklisted button: '{button_text}'")
                        continue
                    
                    # Check if button text is in allowed list (continue/proceed buttons)
                    is_allowed = any(allowed_text in button_text for allowed_text in allowed_button_texts)
                    if is_allowed:
                        print(f"Found authorized proceed button: '{button_text}'")
                        print("Clicking authorization button...")
                        
                        # Scroll button into view and click
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        button.click()
                        time.sleep(3)
                        
                        print("Authorization button clicked successfully")
                        return True
                        
                except Exception as e:
                    print(f"Error checking button: {e}")
                    continue
            
            # If no authorization button found, check if we're already back at contest site
            current_url = self.driver.current_url
            if "disanketnoi.vn" in current_url:
                print("No authorization needed - already back at contest site")
                return True
            
            print("No valid authorization buttons found")
            return True
            
        except Exception as e:
            print(f"Error handling authorization: {e}")
            return False
    
    def handle_existing_login(self):
        """
        Check if user is already logged in and logout if needed
        
        Returns:
            bool: True if logout was successful or no logout needed, False if failed
        """
        try:
            print("Checking for existing login...")
            
            # Look for logout button/link
            logout_selectors = [
                "a:contains('Đăng xuất')",           # Vietnamese logout
                "a:contains('Logout')",              # English logout  
                "a:contains('Sign out')",            # Alternative English
                ".logout",                           # Common logout class
                ".sign-out",                         # Alternative class
                "[href*='logout']",                  # Href containing logout
                ".jet-auth-links__item:contains('Đăng xuất')",  # Specific to this site structure
            ]
            
            logout_found = False
            for selector in logout_selectors:
                try:
                    logout_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for logout_btn in logout_elements:
                        if logout_btn.is_displayed():
                            logout_text = logout_btn.text.strip()
                            if 'Đăng xuất' in logout_text or 'Logout' in logout_text or 'Sign out' in logout_text:
                                print(f"Found existing login - logout button: '{logout_text}'")
                                print("Clicking logout to start fresh...")
                                logout_btn.click()
                                time.sleep(3)  # Wait for logout to complete
                                logout_found = True
                                break
                except:
                    continue
                
                if logout_found:
                    break
            
            if logout_found:
                print("Successfully logged out from existing session")
                time.sleep(2)  # Additional wait for page to update
            else:
                print("No existing login found or already logged out")
            
            return True
            
        except Exception as e:
            print(f"Error handling existing login: {e}")
            return True  # Continue anyway
    
    def redirect_to_target_page(self, target_url="https://disanketnoi.vn/bai-du-thi/ruoc-gom/"):
        """
        Redirect to the target contest page after login
        
        Args:
            target_url (str): The URL to redirect to
            
        Returns:
            bool: True if redirect successful, False otherwise
        """
        try:
            current_url = self.driver.current_url
            
            # Check if we're already on the target page
            if target_url in current_url:
                print(f"Already on target page: {target_url}")
                return True
            
            # Check if we were redirected to main page or somewhere else
            if "disanketnoi.vn" in current_url and target_url not in current_url:
                print(f"Redirected to main page, navigating to target: {target_url}")
                self.driver.get(target_url)
                time.sleep(3)  # Wait for page to load
                
                # Verify we're on the correct page
                new_url = self.driver.current_url
                if target_url in new_url:
                    print("Successfully redirected to target page")
                    return True
                else:
                    print(f"Redirect may have failed. Current URL: {new_url}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error redirecting to target page: {e}")
            return False
    
    def auto_vote_all_accounts(self):
        """
        Automatically cycle through all Google accounts and vote with available ones
        
        Returns:
            int: Number of successful votes
        """
        try:
            print("Starting automatic voting cycle for all accounts...")
            print(f"Previously voted accounts: {len(self.voted_accounts)}")
            
            # Continue until all available accounts are processed
            max_attempts = 50  # Safety limit to prevent infinite loops
            attempt_count = 0
            consecutive_no_accounts = 0  # Track consecutive attempts with no available accounts
            
            while attempt_count < max_attempts:
                attempt_count += 1
                print(f"\n--- Voting Attempt {attempt_count} ---")
                
                # Step 1: Navigate to contest page
                url = "https://disanketnoi.vn/bai-du-thi/ruoc-gom/"
                print(f"Navigating to: {url}")
                self.driver.get(url)
                time.sleep(3)
                
                # Step 2: Handle existing login (logout if already logged in)
                self.handle_existing_login()
                
                # Step 3: Find and click login trigger
                print("Looking for login trigger button...")
                try:
                    login_trigger = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".jet-auth-links__item"))
                    )
                    
                    button_text = login_trigger.text.strip()
                    if "Đăng nhập" in button_text:
                        print("Clicking login trigger...")
                        login_trigger.click()
                        time.sleep(3)
                    else:
                        print(f"Login button text unexpected: '{button_text}'")
                        continue
                        
                except Exception as e:
                    print(f"Could not find login trigger: {e}")
                    continue
                
                # Step 4: Find and click Google sign-in button
                try:
                    google_btn = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".mo_btn-google.login-button"))
                    )
                    print("Clicking Google sign-in...")
                    google_btn.click()
                    time.sleep(5)
                except Exception as e:
                    print(f"Could not find Google sign-in button: {e}")
                    continue
                
                # Step 5: Select available account  
                if "accounts.google.com" in self.driver.current_url:
                    success, email, index = self.select_google_account_automatically(start_from_index=0)
                    
                    if not success:
                        consecutive_no_accounts += 1
                        print(f"No available accounts found in this attempt. (Consecutive: {consecutive_no_accounts})")
                        print(f"Current status - Successful votes: {self.successful_votes}")
                        print(f"Voted accounts: {len(self.voted_accounts)}, Unusable accounts: {len(self.unusable_accounts)}")
                        
                        # If we've had several consecutive attempts with no accounts, we're likely done
                        if consecutive_no_accounts >= 3:
                            print("Multiple consecutive attempts found no available accounts.")
                            print("All accounts have likely been processed!")
                            print(f"Total successful votes: {self.successful_votes}")
                            print(f"Total voted accounts: {len(self.voted_accounts)}")  
                            print(f"Total unusable accounts: {len(self.unusable_accounts)}")
                            break  # Exit the loop - all accounts processed
                        
                        print("Retrying in next attempt to find available accounts...")
                        continue  # Continue to next attempt instead of breaking
                    
                    current_email = email
                    consecutive_no_accounts = 0  # Reset counter since we found an account
                    print(f"Selected account: {current_email}")
                    
                elif "disanketnoi.vn" in self.driver.current_url:
                    print("Already logged in! Checking current account...")
                    consecutive_no_accounts = 0  # Reset counter since we have an account
                    current_email = "current_user"  # We don't know the email in this case
                else:
                    print(f"Unexpected redirect: {self.driver.current_url}")
                    continue
                
                # Step 6: Check if account already voted (this should be rare since we filter them)
                time.sleep(3)  # Wait for page to load
                already_voted = self.check_if_account_already_voted()
                
                if already_voted:
                    if current_email and current_email != "current_user":
                        self.add_voted_account(current_email)
                    print("Account already voted, trying next account...")
                    continue
                
                # Step 7: Vote with this account
                print(f"Attempting to vote with account: {current_email}")
                vote_success = self.click_vote_button()
                
                if vote_success:
                    self.successful_votes += 1
                    if current_email and current_email != "current_user":
                        self.add_voted_account(current_email)
                    print(f"Vote successful! Total votes: {self.successful_votes}")
                    print("Continuing to next account...")
                    
                else:
                    print("Vote failed, trying next account...")
                    # Don't add failed votes to voted accounts - let them be retried
                
                # Small delay between attempts
                time.sleep(2)
            
            print(f"\nVoting cycle completed!")
            print(f"Successful votes: {self.successful_votes}")
            print(f"Processed accounts: {len(self.voted_accounts)}")
            print(f"Unusable accounts: {len(self.unusable_accounts)}")
            print(f"Voted accounts: {list(self.voted_accounts)}")
            if self.unusable_accounts:
                print(f"Unusable accounts: {list(self.unusable_accounts)}")
            
            # Final save of both account lists
            self.save_voted_accounts()
            self.save_unusable_accounts()
            
            return self.successful_votes
            
        except KeyboardInterrupt:
            print("\nVoting cycle stopped by user")
            # Save both account lists even when interrupted
            self.save_voted_accounts()
            self.save_unusable_accounts()
            return self.successful_votes
        except Exception as e:
            print(f"Error in voting cycle: {e}")
            # Save both account lists even when there's an error
            self.save_voted_accounts()
            self.save_unusable_accounts()
            return self.successful_votes
    
    def test_login_flow(self):
        try:
            print("Starting enhanced login flow test...")
            
            # Step 1: Navigate to contest page
            url = "https://disanketnoi.vn/bai-du-thi/ruoc-gom/"
            print(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # Step 1.5: Handle existing login (logout if already logged in)
            self.handle_existing_login()
            
            # Step 2: Find and click login trigger
            print("Looking for login trigger button...")
            login_trigger = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".jet-auth-links__item"))
            )
            
            button_text = login_trigger.text.strip()
            print(f"✅ Found login trigger: '{button_text}'")
            
            if "Đăng nhập" in button_text:
                print("🖱️  Clicking login trigger...")
                login_trigger.click()
                time.sleep(3)
                
                # Step 3: Find Google sign-in button
                print("Looking for Google sign-in button...")
                google_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".mo_btn-google.login-button"))
                )
                
                google_text = google_btn.text.strip()
                print(f"✅ Found Google sign-in button: '{google_text}'")
                
                print("🎉 Login flow test SUCCESSFUL!")
                print("📝 Both elements found and clickable")
                
                # Step 4: Test Google sign-in and account selection
                user_input = input("\n🤔 Do you want to test automatic account selection? (y/n): ")
                if user_input.lower() == 'y':
                    print("🖱️  Clicking Google sign-in...")
                    google_btn.click()
                    time.sleep(5)
                    print(f"🌐 Current URL: {self.driver.current_url}")
                    
                    # Check if we're at Google account selection
                    if "accounts.google.com" in self.driver.current_url:
                        print("🔐 At Google account selection page")
                        
                        # Test automatic account selection
                        success, email, index = self.select_google_account_automatically(start_from_index=0)
                        
                        if success:
                            print(f"✅ Successfully logged in with: {email}")
                            
                            # Check if this account has already voted
                            time.sleep(3)  # Wait for page to load
                            already_voted = self.check_if_account_already_voted()
                            
                            if already_voted:
                                print(f"⚠️  Account {email} has already voted - would skip in automation")
                            else:
                                print(f"✅ Account {email} is ready to vote!")
                                
                                # Test vote functionality
                                test_vote = input("🗳️  Do you want to test voting with this account? (y/n): ")
                                if test_vote.lower() == 'y':
                                    vote_success = self.click_vote_button()
                                    if vote_success:
                                        print("🎉 Vote test successful!")
                                    else:
                                        print("❌ Vote test failed")
                                        
                        else:
                            print("❌ Failed to automatically select account")
                            
                    elif "disanketnoi.vn" in self.driver.current_url:
                        print("✅ Already logged in! Redirected back to contest site")
                        
                        # Check vote status for current account
                        already_voted = self.check_if_account_already_voted()
                        if already_voted:
                            print("⚠️  Current account has already voted")
                        else:
                            print("✅ Current account is ready to vote!")
                            
                            # Test vote functionality
                            test_vote = input("🗳️  Do you want to test voting with current account? (y/n): ")
                            if test_vote.lower() == 'y':
                                vote_success = self.click_vote_button()
                                if vote_success:
                                    print("🎉 Vote test successful!")
                                else:
                                    print("❌ Vote test failed")
                
            else:
                print(f"❌ Button text doesn't match expected 'Đăng nhập': '{button_text}'")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            
        finally:
            keep_open = input("\n🔒 Keep browser open for manual testing? (y/n): ")
            if keep_open.lower() != 'y':
                self.driver.quit()
                print("Browser closed")

if __name__ == "__main__":
    print("Contest Voting Automation")
    print("=" * 50)
    print("This script will automatically vote with all your Google accounts.")
    print("")
    print()
    
    try:
        # Create the voting bot
        bot = ContestVotingBot()
        
        # Start the automated voting process
        print("Starting automated voting process...")
        successful_votes = bot.auto_vote_all_accounts()
        
        print(f"\nAutomation completed!")
        print(f"Total successful votes: {successful_votes}")
        print(f"Accounts processed: {len(bot.voted_accounts)}")
        
        if bot.voted_accounts:
            print(f"Voted accounts: {list(bot.voted_accounts)}")
                
    except KeyboardInterrupt:
        print("\nAutomation stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("Please try running the script again")
    
    finally:
        # Ensure data is saved before exiting
        try:
            if 'bot' in locals():
                bot.save_voted_accounts()
                bot.save_unusable_accounts()
                if bot.driver:
                    bot.driver.quit()
        except:
            pass
        input("\nPress Enter to exit...")
