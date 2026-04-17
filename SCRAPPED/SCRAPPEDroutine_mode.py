# def routine_mode():
#     """Routine mode: brushing teeth, cleaning mouth, washing face"""
#     global mode_active, mode_stop_event, tap_on
    
#     mode_active = True
#     print("=" * 50)
#     print("ROUTINE MODE STARTED")
#     print("=" * 50)
    
#     try:
#         # Phase 1: Wet toothbrush (2 seconds water)
#         print("[Phase 1/5] Wetting toothbrush...")
#         notification_sequence("start")
#         set_led('blue', 1)
#         pi.write(VALVE_PIN, 1)
#         tap_on = True
        
#         for remaining in range(2, 0, -1):
#             if mode_stop_event.is_set():
#                 return
#             print(f"  Wetting: {remaining}...")
#             time.sleep(1)
        
#         pi.write(VALVE_PIN, 0)
#         tap_on = False
#         print("[Phase 1/5] Complete. Brush teeth for 30 seconds")
        
#         # Phase 2: Brush teeth (30 seconds no water)
#         for remaining in range(30, 0, -1):
#             if mode_stop_event.is_set():
#                 return
#             if remaining <= 10:
#                 print(f"  Brushing: {remaining} seconds remaining...")
#                 countdown_notification(remaining)
#             time.sleep(1)
        
#         # Phase 3: Rinse mouth and wet face (40 seconds water)
#         print("[Phase 3/5] Rinsing mouth and wetting face...")
#         notification_sequence("start")
#         set_led('blue', 1)
#         pi.write(VALVE_PIN, 1)
#         tap_on = True
        
#         for remaining in range(40, 0, -1):
#             if mode_stop_event.is_set():
#                 pi.write(VALVE_PIN, 0)
#                 tap_on = False
#                 return
#             print(f"  Rinsing: {remaining} seconds remaining...")
#             countdown_notification(remaining)
#             time.sleep(1)
        
#         pi.write(VALVE_PIN, 0)
#         tap_on = False
        
#         # Phase 4: Wash face (60 seconds water)
#         print("[Phase 4/5] Washing face...")
#         notification_sequence("start")
#         set_led('green', 1)
#         pi.write(VALVE_PIN, 1)
#         tap_on = True
        
#         for remaining in range(60, 0, -1):
#             if mode_stop_event.is_set():
#                 pi.write(VALVE_PIN, 0)
#                 tap_on = False
#                 return
#             print(f"  Face wash: {remaining} seconds remaining...")
#             countdown_notification(remaining)
#             time.sleep(1)
        
#         pi.write(VALVE_PIN, 0)
#         tap_on = False
        
#         # Phase 5: Cleanup (60 seconds no water)
#         print("[Phase 5/5] Cleanup time - Tidy up the area...")
#         set_led('green', 1)
#         for remaining in range(60, 0, -1):
#             if mode_stop_event.is_set():
#                 return
#             if remaining <= 10:
#                 print(f"  Cleanup: {remaining} seconds remaining...")
#             time.sleep(1)
        
#         print("=" * 50)
#         print("ROUTINE MODE COMPLETE!")
#         print("=" * 50)
#         notification_sequence("end")
        
#     finally:
#         pi.write(VALVE_PIN, 0)
#         tap_on = False
#         set_led('off')
#         mode_active = False