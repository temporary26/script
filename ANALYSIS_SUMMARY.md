# 🎯 DISANKETNOI.VN ANALYSIS SUMMARY

## 🔍 **What We Know So Far:**

### **Website Information:**
- **URL**: https://disanketnoi.vn/bai-du-thi/ruoc-gom/
- **Type**: Vietnamese contest/voting website
- **Platform**: WordPress with Elementor page builder
- **Language**: Vietnamese ("bài dự thi" = contest entry, "rước gồm" = contest name)

### **Technical Stack:**
- **CMS**: WordPress
- **Page Builder**: Elementor 
- **Google Integration**: Google Site Kit
- **AJAX**: WordPress admin-ajax.php
- **REST API**: WordPress JSON API (/wp-json/)

### **Authentication System:**
- **Google OAuth Client ID**: `538377308973...apps.googleusercontent.com`
- **OAuth Endpoint**: `https://disanketnoi.vn/quantri-login/?action=googlesitekit_auth`
- **Mechanism**: **Hidden/Revealed Login** (button appears after clicking another button)

### **Forms Found:**
- **1 main form**:
  - Action: `https://disanketnoi.vn/bai-du-thi/ruoc-gom/`
  - Method: POST
  - Class: `elementor-form`
  - 5 inputs + 1 button

---

## 🎯 **Current Challenge:**

The **Google sign-in button is hidden** and only appears after clicking a trigger button. Our automated analysis hasn't identified the exact trigger mechanism yet.

---

## 🚀 **Next Steps Options:**

### **Option 1: Manual Exploration (Recommended)**
Run the manual exploration tool to identify the exact flow:

```bash
python manual_exploration.py
```

This will:
1. Open a browser window
2. Let you manually find the trigger button
3. Click it to reveal Google sign-in
4. Capture the OAuth URL and configuration
5. Document the exact mechanism

### **Option 2: Direct OAuth Implementation**
If you can provide the OAuth details, we can skip the trigger and implement direct authentication:

**What we need:**
- The exact OAuth URL
- client_id (we have: `538377308973...`)
- redirect_uri 
- scope
- Any required state/nonce parameters

### **Option 3: API-First Approach**
Test the backend endpoints directly:

```bash
# Test WordPress AJAX endpoints
POST https://disanketnoi.vn/wp-admin/admin-ajax.php

# Test REST API for voting
POST https://disanketnoi.vn/wp-json/wp/v2/bai-du-thi/5030

# Test Google Site Kit auth
GET https://disanketnoi.vn/quantri-login/?action=googlesitekit_auth
```

---

## 🔑 **Key Information Needed:**

### **For OAuth Implementation:**
1. **Complete OAuth URL** with all parameters
2. **Redirect URI** - where Google sends users back
3. **Scope** - what permissions are requested
4. **State/Nonce** - any CSRF protection tokens

### **For Voting Implementation:**
1. **Vote endpoint** - the API that receives votes
2. **Required headers** - authentication, CSRF tokens
3. **Vote payload** - what data to send
4. **Rate limiting** - how often votes can be submitted

### **For Session Management:**
1. **Session cookies** - how authentication is maintained
2. **Token format** - how auth tokens are structured
3. **Expiration** - how long sessions last

---

## 🎮 **Automation Strategy:**

Once we understand the mechanism, we can implement:

### **Phase 1: Authentication**
```python
# 1. Get OAuth URL with proper parameters
# 2. Handle Google OAuth flow programmatically
# 3. Capture and store authentication tokens
# 4. Maintain session cookies
```

### **Phase 2: Voting**
```python
# 1. Find the vote endpoint
# 2. Submit votes with proper authentication
# 3. Handle any CSRF tokens
# 4. Implement rate limiting
```

### **Phase 3: Multi-Account**
```python
# 1. Cycle through multiple Google accounts
# 2. Manage separate sessions
# 3. Track voting history
# 4. Handle account rotation
```
