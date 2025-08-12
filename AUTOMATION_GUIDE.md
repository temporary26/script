# 🤖 Contest Automation Setup Guide

## 📋 **Recommended Approach: Selenium WebDriver**

Based on your requirements (login → click button → check result → logout → repeat), **Selenium WebDriver** is the best choice because:

### ✅ **Why Selenium?**
1. **Handles JavaScript**: The site uses Elementor (heavy JS), Selenium can handle dynamic content
2. **Google OAuth**: Can automate the complete OAuth flow including 2FA if needed
3. **Session Management**: Properly handles cookies and session state
4. **Element Interaction**: Can find hidden elements and wait for them to appear
5. **Multi-Account Support**: Easy to cycle through different Google accounts

### ❌ **Why NOT Other Approaches?**
- **Requests + BeautifulSoup**: Won't work because the login button is hidden via JavaScript
- **Direct API calls**: Google OAuth requires browser-based flow for security
- **Playwright**: Overkill for this use case, Selenium is more stable for login automation

---

## 🚀 **Setup Instructions**

### **1. Install Dependencies**
```powershell
pip install -r requirements.txt
```

### **2. Install Chrome WebDriver**
Download ChromeDriver from: https://chromedriver.chromium.org/
Or use automatic management in the script.

### **3. Configure Accounts**
Edit the `accounts` list in `automation_strategy.py`:
```python
accounts = [
    ("your-email1@gmail.com", "password1"),
    ("your-email2@gmail.com", "password2"),
]
```

### **4. Test Run**
```powershell
python automation_strategy.py
```

---

## 🎯 **Script Features**

### **Phase 1: Navigation & Login**
- Navigates to contest page
- Finds the hidden login trigger button
- Handles Google OAuth flow
- Manages session cookies

### **Phase 2: Action Execution**
- Clicks target button after login
- Waits for action completion
- Validates result/response

### **Phase 3: Cleanup & Rotation**
- Logs out properly
- Clears session data
- Rotates to next account
- Implements delays to avoid detection

---

## ⚙️ **Customization Options**

### **Headless Mode**
```python
bot = ContestAutomator(headless=True)  # No browser window
```

### **Custom Delays**
```python
time.sleep(5)  # Adjust delays between actions
```

### **Specific Button Targeting**
Update selectors in the script based on your site inspection:
```python
target_selectors = [
    ".your-specific-button-class",
    "#your-button-id"
]
```

### **Result Validation**
Customize success indicators:
```python
success_indicators = [
    ".success-message",
    "text:contains('voted successfully')"
]
```

---

## 🔧 **Advanced Configuration**

### **Stealth Options** (Anti-Detection)
```python
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
```

### **Proxy Support** (If Needed)
```python
chrome_options.add_argument('--proxy-server=http://proxy:port')
```

### **User Data Directory** (Persistent Sessions)
```python
chrome_options.add_argument("--user-data-dir=./chrome-profile")
```

---

## 📊 **Monitoring & Logging**

The script includes comprehensive logging:
- **Console output**: Real-time progress
- **Log file**: `contest_automation.log` for detailed tracking
- **Success tracking**: Counts successful actions
- **Error handling**: Graceful failure recovery

---

## 🚨 **Important Considerations**

### **Rate Limiting**
- Add appropriate delays between actions
- Monitor for CAPTCHA or rate limiting
- Implement exponential backoff if needed

### **Account Security**
- Use app-specific passwords for Google accounts
- Consider 2FA handling
- Rotate accounts to avoid suspension

### **Site Changes**
- The script may need updates if the site structure changes
- Monitor for new anti-bot measures
- Update selectors as needed

### **Legal Compliance**
- Ensure compliance with site terms of service
- Respect rate limits and fair usage
- Consider the ethical implications

---

## 🎪 **Alternative Approaches (If Selenium Fails)**

### **1. Browser Extension**
Create a Chrome extension to automate actions:
- More resistant to detection
- Can run in background
- Persistent across browser sessions

### **2. Puppeteer/Playwright**
If Selenium detection becomes an issue:
```javascript
// Puppeteer example
const browser = await puppeteer.launch();
const page = await browser.newPage();
```

### **3. API Reverse Engineering**
If all else fails, reverse engineer the API:
- Capture network requests during manual actions
- Replicate the exact HTTP calls
- Handle authentication tokens manually

---

## 🔍 **Next Steps**

1. **Test the basic script** with one account
2. **Inspect the actual site** to update selectors
3. **Fine-tune delays** and error handling
4. **Scale up** with multiple accounts
5. **Monitor and adjust** based on results
