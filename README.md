# pkpd-smart-tap
Python code for running the hardware of the Auraflow smart tap on a Raspberry Pi 02w. 
Open the auraflow repository then run tap_logic.py, which is the main program, it calls functions in app_complete.py which runs Flask server and API endpoints, and global variables from config.py. 
On its own, the tap is still usable with IR sensor and waterflow logic. To connect it with the app, connect the RPI to the same wifi network as the android device with the app. 
The SCRAPPED and old_versions contain scrapped and outdated code.
