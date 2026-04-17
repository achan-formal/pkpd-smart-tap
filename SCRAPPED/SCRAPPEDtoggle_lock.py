# def toggle_lock():
#     """Toggle lock mode"""
#     global lock_enabled
#     lock_enabled = not lock_enabled
#     if lock_enabled:
#         print("🔒 Lock mode: ENABLED - Tap is locked")
#         set_led('red', 1)
#         if tap_on:
#             pi.write(VALVE_PIN, 0)
#             global tap_on
#             tap_on = False
#     else:
#         print("🔓 Lock mode: DISABLED - Tap unlocked")
#         set_led('off')
#     return lock_enabled