# def calibrate_flow_sensor(known_volume_liters):
#     """
#     Calibrate the flow sensor using a known volume of water.
#     Run this function with a measured amount of water (e.g., 1 liter)
#     to adjust the calibration factor for accuracy.
    
#     IMPLEMENTED BY: Tariq Shahmeer (20297244)
#     """
#     global flow_calibration_factor, flow_count
    
#     print("=" * 50)
#     print("FLOW SENSOR CALIBRATION MODE")
#     print(f"Calibrating with {known_volume_liters} liters...")
#     print("Press ENTER to start, then run exactly that amount of water through the sensor.")
#     print("=" * 50)
    
#     input("Press ENTER when ready to start calibration...")
    
#     # Reset counter
#     start_count = flow_count
#     print("Counting pulses... Press ENTER when done.")
#     input("Press ENTER to finish calibration...")
    
#     end_count = flow_count
#     pulses_received = end_count - start_count
    
#     if pulses_received > 0:
#         # Calculate new calibration factor
#         new_factor = pulses_received / known_volume_liters
#         print(f"\nCalibration Results:")
#         print(f"  Pulses received: {pulses_received}")
#         print(f"  Known volume: {known_volume_liters} L")
#         print(f"  Old calibration factor: {flow_calibration_factor} pulses/L")
#         print(f"  New calibration factor: {new_factor} pulses/L")
        
#         # Ask user if they want to apply
#         confirm = input("\nApply new calibration factor? (y/n): ").lower()
#         if confirm == 'y':
#             flow_calibration_factor = new_factor
#             print(f"Calibration factor updated to: {flow_calibration_factor}")
#             # Optionally save to config file
#             save_calibration_config()
#         else:
#             print("Calibration cancelled. Using existing factor.")
#     else:
#         print("No pulses detected. Check sensor connection and water flow.")

# def save_calibration_config():
#     """Save calibration settings to a config file"""
#     config = {
#         'calibration_factor': flow_calibration_factor,
#         'last_calibration': time.time(),
#         'calibrated_by': 'Tariq Shahmeer (20297244)'
#     }
#     try:
#         with open('flow_calibration.json', 'w') as f:
#             json.dump(config, f, indent=2)
#         print("Calibration settings saved.")
#     except Exception as e:
#         print(f"Error saving calibration: {e}")

# def load_calibration_config():
#     """Load calibration settings from config file"""
#     global flow_calibration_factor
#     try:
#         with open('flow_calibration.json', 'r') as f:
#             config = json.load(f)
#             flow_calibration_factor = config.get('calibration_factor', 450.0)
#             print(f"Loaded calibration factor: {flow_calibration_factor}")
#     except FileNotFoundError:
#         print("No calibration file found. Using default factor.")
#     except Exception as e:
#         print(f"Error loading calibration: {e}")

# -----------------------------------------------------------
# def api_calibrate_sensor(known_volume_liters):
#     """API function to calibrate flow sensor"""
#     try:
#         calibrate_flow_sensor(float(known_volume_liters))
#         return {
#             "status": "success", 
#             "message": f"Calibration completed",
#             "new_calibration_factor": flow_calibration_factor
#         }
#     except Exception as e:
#         return {"status": "error", "message": str(e)}