================================================================================
                      UMTK GUI - macOS Setup Instructions
================================================================================

When you download the UMTK GUI application from the internet (including from 
GitHub releases), macOS automatically adds a security flag called "quarantine" 
to protect your computer. This is normal behavior, but it means you need to 
take one extra step before the app will work properly.

================================================================================
Running App for the First Time
================================================================================

1. RIGHT-CLICK (or Control-click) on the UMTK GUI app
2. Hold "Shift" Key and Select "Open" from the menu
3. If a warning appears that reads "umtk-ui not opened ..." and there is not a "Open Anyway" Button
4. Click "Done" and follow steps below

================================================================================
Allow umtk-ui In Gatekeeper
================================================================================

If you have attempted to run umtk-ui and is unsuccessful.

1. Go to your mac's "Settings" App and search for "Gatekeeper"
2. There should be a entry in the settings app with a messages that reads like:
   "umtk-ui" was blocked to protect your Mac. 
   Click the "Open Anyway" button.
3. You will see a popup, with a "Open Anyway" button. Click "Open Anyway"
4. You will be asked to authorize this action by supplying your password, this is safe to do.
5. The UMTK UI app will now start.
6. Your mac will remember this setting and nolonger block umtk-ui in the future.


================================================================================
Alternative Method using Terminal
================================================================================

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
Why Does This Happen?
================================================================================

This security feature is called "Gatekeeper" and it's designed to protect 
your Mac from potentially harmful software. Since the UMTK GUI app isn't 
signed with an Apple Developer certificate (which costs money and requires 
going through Apple's approval process), macOS treats it as "unknown" software.

The app is completely safe to use - removing the quarantine flag simply tells 
macOS that you trust this particular application.

This security restriction only applies to apps downloaded from the internet. 
If you build the UMTK GUI yourself from source code, you won't encounter 
this issue.