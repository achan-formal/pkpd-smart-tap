from flask import Flask, request, jsonify
import config

app = Flask(__name__)

# ------------------------ State Variables ---------------------------
# Store state instead of physical GPIO effects
# config.api_tap_on = False      # Current water tap state (True = ON, False = OFF)
# config.locked = False          # Lock state (True = LOCKED, False = UNLOCKED)
# config.water_usage_log = 0.0       # Total water usage in liters (float)
# config.wash = False

# ------------------------ HTTP Endpoints ---------------------------

@app.route('/water/on', methods=['GET', 'POST'])
def water_on():
    """Turn water ON (stores in variable)"""
    config.api_tap_on = True

@app.route('/water/off', methods=['GET', 'POST'])
def water_off():
    """Turn water OFF (stores in variable)"""
    config.api_tap_on = False

@app.route('/water/usage', methods=['GET'])
def get_water_usage():
    """GET: Return water usage log (float)"""
    return jsonify([config.water_usage_log])

@app.route('/water/status', methods=['GET'])
def get_water_status():
    """GET: Return whether the tap is currently on (bool)"""
    return jsonify([config.api_tap_on])

@app.route('/lock', methods=['POST'])
def lock_tap():
    """Lock the water tap"""
    config.api_tap_on = False
    config.config.locked = True

@app.route('/unlock', methods=['POST'])
def unlock_tap():
    """Unlock the water tap"""
    config.config.locked = False

@app.route('/wash/start', methods=['GET', 'POST'])
def wash_start():
    config.wash = True

@app.route('/wash/stop', methods=['GET', 'POST'])
def wash_stop():
    config.wash = False

def run_flask():
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ------------------------ Main Entry Point ---------------------------

if __name__ == '__main__':
    print("=" * 50)
    print("🚰 Smart Faucet Server (Simulation Mode)")
    print("=" * 50)
    print("\n📊 State Variables (no physical GPIO effects):")
    print(f"   Water state: {config.api_tap_on}")
    print(f"   Lock state: {config.config.locked}")
    print(f"   Water usage log: {config.water_usage_log}L")
    
    print("\n📱 Available Endpoints:")
    print("   GET/POST  /water/on          - Turn water ON")
    print("   GET/POST  /water/off         - Turn water OFF")
    print("   GET       /water/usage       - Get water usage log (float)")
    print("   GET       /water/status      - Get tap on/off status (bool)")
    print("   GET/POST  /lock              - Get/Set lock state (bool)")
    print("   POST      /water/reset       - Reset water usage to 0")
    print("   GET       /status            - Get full system status")
    print("   POST      /wash/start        - Simulate wash start")
    print("   POST      /wash/stop         - Stop wash")
    
    print("\n🔧 Example API calls:")
    print("   curl -X POST http://localhost:5000/lock -H 'Content-Type: application/json' -d '{\"lock\": true}'")
    print("   curl http://localhost:5000/water/status")
    print("   curl http://localhost:5000/water/usage")
    
    print("\n" + "=" * 50)
    print("✅ Server starting on http://0.0.0.0:5000")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)