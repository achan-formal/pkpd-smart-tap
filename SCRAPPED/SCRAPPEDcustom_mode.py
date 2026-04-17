# def custom_mode(mode_name):
#     """Execute custom mode with user-defined settings"""
#     global mode_active, mode_stop_event, tap_on
    
#     if mode_name not in custom_modes:
#         print(f"Custom mode '{mode_name}' not found")
#         return
    
#     mode_active = True
#     settings = custom_modes[mode_name]
#     duration = settings['duration']
    
#     print("=" * 50)
#     print(f"CUSTOM MODE: {settings['name']}")
#     print(f"Duration: {duration} seconds")
#     print("=" * 50)
    
#     try:
#         notification_sequence("start")
#         set_led('blue', 1)
#         pi.write(VALVE_PIN, 1)
#         tap_on = True
        
#         # Countdown with notifications
#         for remaining in range(duration, 0, -1):
#             if mode_stop_event.is_set():
#                 pi.write(VALVE_PIN, 0)
#                 tap_on = False
#                 return
#             print(f"  {remaining} seconds remaining...")
#             countdown_notification(remaining)
#             time.sleep(1)
        
#         pi.write(VALVE_PIN, 0)
#         tap_on = False
#         print(f"=" * 50)
#         print(f"CUSTOM MODE '{settings['name']}' COMPLETE!")
#         print("=" * 50)
#         notification_sequence("end")
        
#     finally:
#         pi.write(VALVE_PIN, 0)
#         tap_on = False
#         set_led('off')
#         mode_active = False

# # ------------------------ Custom Mode Management ---------------------------
# def load_custom_modes():
#     """Load custom modes from file"""
#     global custom_modes
#     if os.path.exists(CUSTOM_MODES_FILE):
#         try:
#             with open(CUSTOM_MODES_FILE, 'r') as f:
#                 custom_modes = json.load(f)
#             print(f"Loaded {len(custom_modes)} custom modes")
#         except Exception as e:
#             print(f"Error loading custom modes: {e}")
#             custom_modes = {}
#     else:
#         custom_modes = {}
#         print("No custom modes file found. Starting fresh.")

# def save_custom_modes():
#     """Save custom modes to file"""
#     try:
#         with open(CUSTOM_MODES_FILE, 'w') as f:
#             json.dump(custom_modes, f, indent=2)
#         print(f"Saved {len(custom_modes)} custom modes")
#         return True
#     except Exception as e:
#         print(f"Error saving custom modes: {e}")
#         return False

# def add_custom_mode(mode_name, duration):
#     """Add or update a custom mode"""
#     if mode_name in custom_modes:
#         print(f"Updating mode '{mode_name}'")
#     else:
#         print(f"Adding new mode '{mode_name}'")
    
#     custom_modes[mode_name] = {
#         'name': mode_name,
#         'duration': int(duration),
#         'created': time.time()
#     }
#     save_custom_modes()
#     return True

# def delete_custom_mode(mode_name):
#     """Delete a custom mode"""
#     if mode_name in custom_modes:
#         del custom_modes[mode_name]
#         save_custom_modes()
#         print(f"Deleted mode '{mode_name}'")
#         return True
#     return False

# def list_custom_modes():
#     """List all saved custom modes"""
#     if not custom_modes:
#         print("No custom modes saved")
#         return []
#     return list(custom_modes.keys())