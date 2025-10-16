================================================================================
                      UMTK GUI - macOS Setup Instructions
================================================================================

IMPORTANT: Removing Security Restrictions

When you download the UMTK GUI application from the internet (including from 
GitHub releases), macOS automatically adds a security flag called "quarantine" 
to protect your computer. This is normal behavior, but it means you need to 
take one extra step before the app will work properly.

================================================================================
What You'll See
================================================================================

When you first try to run the UMTK GUI app, you might see one of these messages:
• "UMTK GUI cannot be opened because it is from an unidentified developer"
• "UMTK GUI cannot be opened because Apple cannot check it for malicious software"
• The app might not start at all, or crash immediately

================================================================================
Step-by-Step Solution
================================================================================

Don't worry! This is easy to fix. Follow these steps:

STEP 1: Find the Terminal App
-----------------------------
1. Press Cmd + Space to open Spotlight search
2. Type "Terminal" and press Enter
3. A black window with white text will open - this is the Terminal

STEP 2: Navigate to Your Downloaded App
---------------------------------------
1. In the Terminal, you need to tell it where your UMTK GUI app is located
2. If you downloaded it to your DOWNLOADS folder, type this command and press Enter:
   
   cd ~/Downloads

3. If you moved it to your APPLICATIONS folder, type this instead:
   
   cd /Applications

4. If you put it somewhere else, you'll need to adjust the path accordingly

STEP 3: Remove the Quarantine Flag
----------------------------------
1. Type this command in the Terminal (replace "umtk-ui" with the exact name 
   of your app file):
   
   sudo xattr -r -d com.apple.quarantine umtk-ui

2. Press Enter
3. You'll be asked for your Mac's password (the same one you use to log in)
4. Type your password and press Enter (don't worry if you can't see the 
   characters as you type - this is normal)

STEP 4: Try Running the App Again
---------------------------------
1. Close the Terminal window
2. Double-click on the UMTK GUI app
3. It should now start normally!

================================================================================
Alternative Method (If You're Not Comfortable with Terminal)
================================================================================

If you prefer not to use the Terminal, you can try this approach:

1. RIGHT-CLICK (or Control-click) on the UMTK GUI app
2. Select "Open" from the menu
3. If a warning appears, click "Open" again to confirm
4. macOS will remember your choice and allow the app to run in the future

NOTE: This alternative method doesn't always work for all apps, so the 
Terminal method above is more reliable.

================================================================================
Why Does This Happen?
================================================================================

This security feature is called "Gatekeeper" and it's designed to protect 
your Mac from potentially harmful software. Since the UMTK GUI app isn't 
signed with an Apple Developer certificate (which costs money and requires 
going through Apple's approval process), macOS treats it as "unknown" software.

The app is completely safe to use - removing the quarantine flag simply tells 
macOS that you trust this particular application.

================================================================================
Need Help?
================================================================================

If you're still having trouble:

1. DOUBLE-CHECK THE APP NAME: Make sure you're using the exact filename in 
   the Terminal command
2. CHECK THE LOCATION: Ensure you're in the right folder where the app is located
3. TRY THE ALTERNATIVE METHOD: Use the right-click → Open approach described above

If you continue to have issues, please reach out to the UMTK development team 
with details about:
• Your macOS version (Apple menu → About This Mac)
• The exact error message you're seeing
• Where you downloaded the app from

================================================================================

This security restriction only applies to apps downloaded from the internet. 
If you build the UMTK GUI yourself from source code, you won't encounter 
this issue.