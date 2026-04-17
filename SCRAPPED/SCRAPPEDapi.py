# # ------------------------ API Interface Functions ---------------------------
# def api_set_mode(mode_name):
#     """API function to set/start a mode"""
#     if lock_enabled and mode_name != "lock":
#         return {"status": "error", "message": "Tap is locked"}
#     success = start_mode(mode_name)
#     if success:
#         return {"status": "success", "message": f"Mode {mode_name} started"}
#     else:
#         return {"status": "error", "message": f"Cannot start mode {mode_name}"}

# def api_stop_mode():
#     """API function to stop current mode"""
#     success = stop_current_mode()
#     if success:
#         return {"status": "success", "message": "Mode stopped"}
#     return {"status": "info", "message": "No mode running"}

# def api_toggle_lock():
#     """API function to toggle lock mode"""
#     locked = toggle_lock()
#     return {"status": "success", "message": f"Lock mode {'enabled' if locked else 'disabled'}"}

# def api_add_custom_mode(name, duration):
#     """API function to add a custom mode"""
#     try:
#         duration = int(duration)
#         if duration <= 0:
#             return {"status": "error", "message": "Duration must be positive"}
#         if duration > 3600:
#             return {"status": "error", "message": "Duration cannot exceed 1 hour"}
#         success = add_custom_mode(name, duration)
#         if success:
#             return {"status": "success", "message": f"Custom mode '{name}' added with {duration}s"}
#     except ValueError:
#         return {"status": "error", "message": "Duration must be a number"}
#     return {"status": "error", "message": "Failed to add custom mode"}

# def api_delete_custom_mode(name):
#     """API function to delete a custom mode"""
#     success = delete_custom_mode(name)
#     if success:
#         return {"status": "success", "message": f"Custom mode '{name}' deleted"}
#     return {"status": "error", "message": f"Mode '{name}' not found"}

# def api_list_modes():
#     """API function to list all available modes"""
#     available_modes = {
#         "built_in": ["routine", "wash"],
#         "custom": list_custom_modes(),
#         "current_mode": current_mode,
#         "mode_active": mode_active,
#         "lock_enabled": lock_enabled,
#         "water_usage_liters": get_water_usage()
#     }
#     return available_modes

# def api_ir_status():
#     """Get IR sensor status"""
#     detected = gp.input(IR_SENSOR_PIN) == 0
#     return {
#         "ir_detected": detected, 
#         "tap_on": tap_on, 
#         "lock_enabled": lock_enabled,
#         "mode_active": mode_active,
#         "current_mode": current_mode
#     }

# def api_water_usage():
#     """Get water usage data - Extended by Tariq Shahmeer (20297244)"""
#     return {
#         "total_liters": get_water_usage(),
#         "flow_rate_lpm": get_flow_rate(),
#         "count": flow_count,
#         "calibration_factor": flow_calibration_factor,
#         "daily_liters": get_daily_water_usage()
#     }

# def api_reset_water_usage():
#     """Reset water usage counter"""
#     reset_water_usage()
#     return {"status": "success", "message": "Water usage reset"}

# # ------------------------ Flask Server for API ---------------------------
# try:
#     from flask import Flask, request, jsonify
#     from flask_cors import CORS
    
#     app = Flask(__name__)
#     CORS(app)
    
#     @app.route('/api/mode/start', methods=['POST'])
#     def start_mode_route():
#         data = request.json
#         mode = data.get('mode')
#         return jsonify(api_set_mode(mode))
    
#     @app.route('/api/mode/stop', methods=['POST'])
#     def stop_mode_route():
#         return jsonify(api_stop_mode())
    
#     @app.route('/api/lock/toggle', methods=['POST'])
#     def toggle_lock_route():
#         return jsonify(api_toggle_lock())
    
#     @app.route('/api/custom/add', methods=['POST'])
#     def add_custom_route():
#         data = request.json
#         name = data.get('name')
#         duration = data.get('duration')
#         return jsonify(api_add_custom_mode(name, duration))
    
#     @app.route('/api/custom/delete', methods=['POST'])
#     def delete_custom_route():
#         data = request.json
#         name = data.get('name')
#         return jsonify(api_delete_custom_mode(name))
    
#     @app.route('/api/modes/list', methods=['GET'])
#     def list_modes_route():
#         return jsonify(api_list_modes())
    
#     @app.route('/api/ir/status', methods=['GET'])
#     def ir_status_route():
#         return jsonify(api_ir_status())
    
#     @app.route('/api/water/usage', methods=['GET'])
#     def water_usage_route():
#         return jsonify(api_water_usage())
    
#     @app.route('/api/water/reset', methods=['POST'])
#     def water_reset_route():
#         return jsonify(api_reset_water_usage())
    
#     @app.route('/api/status', methods=['GET'])
#     def full_status_route():
#         return jsonify({
#             **api_ir_status(),
#             **api_water_usage(),
#             "custom_modes": list_custom_modes()
#         })
    
#     def run_flask():
#         app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
#     FLASK_AVAILABLE = True
    
# except ImportError:
#     print("⚠️ Flask not installed. API server will not start.")
#     print("Install with: pip install flask flask-cors")
#     FLASK_AVAILABLE = False
#     def run_flask():
#         pass