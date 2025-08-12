# Test script for login flow verification
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as EdgeOptions

class LoginTester:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.browser_choice = None
        self.browser_path = None
        self.profile_path = None
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
    
    def select_browser(self):
        """Let user select which browser to use"""
        browsers = self.get_browser_locations()
        
        print("🌐 Available Browsers:")
        print("=" * 50)
        
        available_browsers = []
        for key, info in browsers.items():
            executable_path, profile_path = self.find_browser_executable(key)
            status = "✅ Available" if executable_path else "❌ Not Found"
            print(f"{len(available_browsers) + 1}. {info['name']} - {status}")
            if executable_path:
                print(f"   📁 Executable: {executable_path}")
                print(f"   👤 Profile: {profile_path}")
                available_browsers.append((key, executable_path, profile_path))
            print()
        
        if not available_browsers:
            print("❌ No supported browsers found!")
            exit(1)
        
        # Let user choose
        while True:
            try:
                choice = input(f"Select browser (1-{len(available_browsers)}): ").strip()
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(available_browsers):
                    self.browser_choice, self.browser_path, self.profile_path = available_browsers[choice_idx]
                    browser_name = browsers[self.browser_choice]["name"]
                    print(f"✅ Selected: {browser_name}")
                    print(f"📁 Using: {self.browser_path}")
                    if self.profile_path:
                        print(f"👤 Profile: {self.profile_path}")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
            except (ValueError, IndexError):
                print("❌ Invalid input. Please enter a number.")
    
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
        
        # Use real profile with saved logins
        use_profile = input("🔑 Use saved profile with logged-in accounts? (y/n): ").strip().lower()
        if use_profile == 'y' and self.profile_path:
            chrome_options.add_argument(f"--user-data-dir={self.profile_path}")
            chrome_options.add_argument("--profile-directory=Default")
            print("✅ Using saved profile - your logged-in accounts will be available!")
        else:
            print("ℹ️  Using clean session - you'll need to log in manually")
        
        # Essential options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Keep browser open after script ends
        chrome_options.add_experimental_option("detach", True)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            
            # Hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"✅ {self.get_browser_locations()[self.browser_choice]['name']} initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing {self.browser_choice}: {e}")
            print("💡 Make sure to close all browser windows first")
            raise
    
    def setup_firefox_driver(self):
        """Setup Firefox WebDriver"""
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        
        firefox_options = FirefoxOptions()
        firefox_options.binary_location = self.browser_path
        
        # Use profile if available
        use_profile = input("🔑 Use saved Firefox profile? (y/n): ").strip().lower()
        if use_profile == 'y' and self.profile_path:
            # Firefox profile setup is more complex
            print("ℹ️  Firefox profile setup requires additional configuration")
        
        try:
            self.driver = webdriver.Firefox(options=firefox_options)
            self.wait = WebDriverWait(self.driver, 15)
            print("✅ Firefox initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing Firefox: {e}")
            print("💡 Make sure geckodriver is installed: pip install selenium[firefox]")
            raise
    
    def test_login_flow(self):
        """Test the complete login flow"""
        try:
            print("🚀 Starting login flow test...")
            
            # Step 1: Navigate to contest page
            url = "https://disanketnoi.vn/bai-du-thi/ruoc-gom/"
            print(f"📍 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # Step 2: Find and click login trigger
            print("🔍 Looking for login trigger button...")
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
                print("🔍 Looking for Google sign-in button...")
                google_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".mo_btn-google.login-button"))
                )
                
                google_text = google_btn.text.strip()
                print(f"✅ Found Google sign-in button: '{google_text}'")
                
                print("🎉 Login flow test SUCCESSFUL!")
                print("📝 Both elements found and clickable")
                
                # Optionally click Google button to test (will redirect to Google)
                user_input = input("\n🤔 Do you want to test clicking Google sign-in? (y/n): ")
                if user_input.lower() == 'y':
                    print("🖱️  Clicking Google sign-in...")
                    google_btn.click()
                    time.sleep(5)
                    print(f"🌐 Current URL: {self.driver.current_url}")
                    
                    # Check if we're at Google OAuth or already logged in
                    if "accounts.google.com" in self.driver.current_url:
                        print("🔐 Redirected to Google OAuth - manual login required")
                    elif "disanketnoi.vn" in self.driver.current_url:
                        print("✅ Already logged in! Redirected back to contest site")
                
            else:
                print(f"❌ Button text doesn't match expected 'Đăng nhập': '{button_text}'")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            
        finally:
            keep_open = input("\n🔒 Keep browser open for manual testing? (y/n): ")
            if keep_open.lower() != 'y':
                self.driver.quit()
                print("👋 Browser closed")

if __name__ == "__main__":
    print("🧪 Login Flow Tester")
    print("=" * 50)
    
    tester = LoginTester()
    tester.test_login_flow()
