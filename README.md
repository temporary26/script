# Auto-vote Python Script

An automated Python script that automatically votes using all the Google accounts saved in the browser you use. 

## Features

- **Multi-Account Support**: Automatically cycles through all available Google accounts in your browser
- **Smart Account Management**: Tracks voted and unusable accounts to avoid duplicates and errors
- **Persistent State**: Saves account status to files for resuming across script runs
- **Browser Compatibility**: Supports Chrome, Brave, Edge, Firefox, and Opera browsers
- **Automated Error Handling**: Skips problematic accounts and continues with others

## Account Handling

The script intelligently manages different account states:

### Voted Accounts
- Accounts that have successfully voted are tracked in `voted_accounts.txt`
- These accounts are automatically skipped in future runs

### Unusable Accounts
- Accounts requiring manual intervention are tracked in `unusable_accounts.txt`
- Includes accounts that require:
  - Password entry
  - Two-factor authentication
  - Identity verification ("Verify it's you")
  - Security checks ("To help keep your account safe...")
- These accounts are automatically skipped to maintain automation flow

### Available Accounts
- Accounts that can be used for voting
- The script will attempt to vote with these accounts automatically

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Required Python packages** (install with `pip install -r requirements.txt`):
   - selenium
   - webdriver-manager (if using Chrome)
3. **Supported browser** installed (Chrome, Brave, Edge, Firefox, or Opera)
4. **Google accounts** already logged into your browser

## Important Setup Requirements

**CRITICAL**: Before running the script, ensure all your Google accounts are properly configured:

1. **All accounts must be logged into your browser**
2. **Make sure every account is usable for sign in** and complete any pending security checkpoints/password verifications.

**Note**: The script runs in fully automated mode and does NOT allow user interaction during execution. Any account requiring manual input will be marked as unusable and skipped.

## Installation

1. Install python either from Microsoft Store or from the official Python website: https://www.python.org/downloads/
2. Clone or download this repository
3. Install required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
   Or run the install script (make sure you have winget installed).
4. Ensure your browser has Google accounts logged in

## Usage

1. Run the script:
   ```cmd
   python script.py
   ```

   or 
   ```powershell
   python .\script.py
   ```
2. Select your preferred browser from the available options
3. The script will automatically:
   - Navigate to the contest website
   - Cycle through available Google accounts
   - Vote with each eligible account
   - Skip voted and unusable accounts


## File Structure

```
PythonTool/
├── script.py                  # Main automation script
├── requirements.txt           # Python dependencies
├── voted_accounts.txt         # List of accounts that have voted
├── unusable_accounts.txt      # List of accounts requiring manual intervention
├── contest_automation.log     # Script execution logs
└── README.md                  # This file
```

## Output Files

### voted_accounts.txt
Contains email addresses of accounts that have successfully voted:
```
user1@gmail.com
user2@gmail.com
user3@gmail.com
```

### unusable_accounts.txt
Contains email addresses of accounts that require manual intervention:
```
user4@gmail.com
user5@gmail.com
```

## Script Behavior

1. **Initialization**: Loads previously voted and unusable accounts from files
2. **Browser Selection**: Prompts user to select available browser
3. **Account Discovery**: Finds all logged-in Google accounts
4. **Voting Loop**: For each available account:
   - Skip if already voted or unusable
   - Attempt to vote
   - Handle authentication prompts
   - Mark account status appropriately
5. **Persistence**: Saves account status to files after each change
6. **Completion**: Reports final statistics and exits

## Error Handling

The script includes robust error handling:
- **Network issues**: Retries failed requests
- **Authentication problems**: Marks accounts as unusable
- **Page loading errors**: Continues with next account
- **Browser crashes**: Saves progress before exit


## Troubleshooting

### Common Issues

1. **"No available accounts found"**
   - Ensure Google accounts are logged into your browser
   - Check that accounts don't require verification

2. **"Browser not found"**
   - Install a supported browser
   - Check browser installation paths

3. **"Script stops after finding unusable account"**
   - This is expected behavior - the script continues with other accounts
   - Check `unusable_accounts.txt` for details

4. **"Accounts require password"**
   - Manually log into accounts in browser
   - Ensure "Stay signed in" is enabled
   - Disable 2FA where possible

### Debug Mode

For troubleshooting, the script provides detailed console output showing:
- Account discovery process
- Voting attempts and results
- Error messages and account status changes
- Final statistics
