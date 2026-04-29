# ----------------------- PINOUT (Based on RPi02w Pinout Diagram) ---------------------------
# 
# Pin Number | Function        | Component     | Description
# -----------|-----------------|---------------|------------------------------------------
# 1          | 3.3V Power      | IR Sensor     | Power for IR sensor
# 2          | 5V Power        | IR Sensor     | 5V power for IR sensor (if needed)
# 3          | GPIO 2 (SDA)    | -             | Available
# 4          | 5V Power        | Flow Sensor   | 5V power for flow sensor
# 5          | GPIO 3 (SCL)    | -             | Available
# 6          | Ground          | Flow Sensor   | Ground for flow sensor
# 7          | GPIO 4          | -             | Available
# 8          | GPIO 14 (UART0 TX)| Flow Sensor | Signal pin for flow sensor
# 9          | Ground          | IR Sensor     | Ground for IR sensor
# 10         | GPIO 15 (UART0 RX)| Valve       | Control pin for solenoid valve
# 11         | GPIO 17         | -             | Available
# 12         | GPIO 18 (PCM CLK)| Buzzer       | Buzzer control
# 13         | GPIO 27         | LED Red       | Red LED for lock/error indication
# 14         | Ground          | -             | Ground
# 15         | GPIO 22         | LED Green     | Green LED for active mode indication
# 16         | GPIO 23         | LED Blue      | Blue LED for mode in progress
# 17         | 3.3V Power      | -             | 3.3V power
# 18         | GPIO 24         | -             | Available
# 19         | GPIO 10 (SPI0 MOSI)| -          | Available
# 20         | Ground          | -             | Ground
# 21         | GPIO 9 (SPI0 MISO)| -          | Available
# 22         | GPIO 25         | -             | Available
# 23         | GPIO 11 (SPI0 SCLK)| -         | Available
# 24         | GPIO 8 (SPI0 CE0)| -           | Available
# 25         | Ground          | -             | Ground
# 26         | GPIO 7 (SPI0 CE1)| -           | Available
# 27         | GPIO 0 (EEPROM SDA)| -         | Available
# 28         | GPIO 1 (EEPROM SCL)| -         | Available
# 29         | GPIO 5          | -             | Available
# 30         | Ground          | -             | Ground
# 31         | GPIO 6          | -             | Available
# 32         | GPIO 12 (PWM0)  | -             | Available
# 33         | GPIO 13 (PWM1)  | -             | Available
# 34         | Ground          | -             | Ground
# 35         | GPIO 19 (PCM FS)| -             | Available
# 36         | GPIO 16         | -             | Available
# 37         | GPIO 26         | -             | Available
# 38         | GPIO 20 (PCM DIN)| -           | Available
# 39         | Ground          | -             | Ground
# 40         | GPIO 21 (PCM DOUT)| -          | Available

# ----------------------- Flow Sensor ----------------------------
# Pin 4: 5V Power
# Pin 6: Ground
# Pin 8: GPIO 14 (UART0 TX) - Signal

# ----------------------- IR Sensor ------------------------------
# Pin 1: 3.3V Power
# Pin 2: 5V Power
# Pin 9: Ground
# Signal: Need to connect to a GPIO pin (using GPIO 2 on Pin 3)

# ----------------------- Solenoid Valve -------------------------
# Pin 10: GPIO 15 - Control pin (via relay)

# ----------------------- Buzzer --------------------------------
# Pin 12: GPIO 18 - Buzzer control

# ----------------------- LEDs -----------------------------------
# Pin 13: GPIO 27 - Red LED (Lock/Error)
# Pin 15: GPIO 22 - Green LED (Active mode)
# Pin 16: GPIO 23 - Blue LED (Mode in progress)

# ===================================================================
# CODE AUTHOR: Tariq Shahmeer (20297244)
# Water flow sensor implementation for AuraFlow Smart Tap System
# ===================================================================

import time
import pigpio
import RPi.GPIO as gp
from time import sleep
import threading
import json
import os

# ------------------------ GPIO Pin Definitions ---------------------------
# Using BOARD numbering to match physical pins

# Flow sensor (using pigpio for interrupt capability)
FLOW_SENSOR_PIN = 8  # Physical pin 8, GPIO 14

# IR sensor
IR_SENSOR_PIN = 3    # Physical pin 3, GPIO 2

# Valve control (via relay)
VALVE_PIN = 10       # Physical pin 10, GPIO 15

# Buzzer
BUZZER_PIN = 12      # Physical pin 12, GPIO 18

# LEDs
LED_RED_PIN = 13     # Physical pin 13, GPIO 27
LED_GREEN_PIN = 15   # Physical pin 15, GPIO 22
LED_BLUE_PIN = 16    # Physical pin 16, GPIO 23

# ------------------------ Global Variables ---------------------------
flow_ttime = 0.0
tap_on = False
current_mode = "default"  # default, routine, wash, custom, lock
lock_enabled = False
custom_modes = {}  # Store custom modes
mode_active = False
mode_thread = None
mode_stop_event = threading.Event()

# Flow sensor counters
flow_count = 0
flow_volume = 0.0  # in liters
# Calibration factor: pulses per liter
# YF-B1 Hall Effect sensor typically outputs ~450 pulses per liter
# Formula: 1 Liter = 450 pulses (adjust after calibration with known volume)
flow_calibration_factor = 450.0  # pulses per liter

# Flow rate tracking variables
last_pulse_time = 0
flow_rate_lpm = 0.0  # liters per minute
pulse_interval_sum = 0.0
pulse_interval_count = 0
FLOW_RATE_SMOOTHING_FACTOR = 0.3  # For exponential moving average

# Custom modes file
CUSTOM_MODES_FILE = "custom_modes.json"

# Water usage history for tracking
water_usage_history = []  # Store timestamps and usage
MAX_HISTORY_ENTRIES = 100

# ------------------------ Flow Sensor Callback ---------------------------
def flow_callback(gpio, level, tick):
    """Callback function for flow sensor pulses"""
    global flow_count, last_pulse_time, flow_rate_lpm
    global pulse_interval_sum, pulse_interval_count
    
    if level == 0:  # Falling edge (when water flows)
        flow_count += 1
        
        # Calculate flow rate from pulse interval
        current_time = time.time()
        if last_pulse_time > 0:
            interval = current_time - last_pulse_time
            if interval > 0:
                # Calculate instantaneous flow rate (L/min)
                # pulses per second = 1/interval
                # liters per second = (1/interval) / calibration_factor
                # liters per minute = (60/interval) / calibration_factor
                inst_flow_rate = (60.0 / interval) / flow_calibration_factor
                
                # Apply exponential moving average for smoothing
                if flow_rate_lpm == 0:
                    flow_rate_lpm = inst_flow_rate
                else:
                    flow_rate_lpm = (FLOW_RATE_SMOOTHING_FACTOR * inst_flow_rate + 
                                    (1 - FLOW_RATE_SMOOTHING_FACTOR) * flow_rate_lpm)
        
        last_pulse_time = current_time

# ------------------------ Water Usage Functions ---------------------------
# IMPLEMENTED BY: Tariq Shahmeer (20297244)
# Water flow sensor data processing and usage tracking

def get_water_usage():
    """Calculate water usage in liters since last reset"""
    global flow_count, flow_volume
    flow_volume = flow_count / flow_calibration_factor
    return flow_volume

def reset_water_usage():
    """Reset water usage counter"""
    global flow_count, flow_volume, water_usage_history
    # Log current usage before reset for history
    current_usage = get_water_usage()
    if current_usage > 0:
        water_usage_history.append({
            'timestamp': time.time(),
            'volume': current_usage,
            'mode': current_mode
        })
        # Keep history size manageable
        while len(water_usage_history) > MAX_HISTORY_ENTRIES:
            water_usage_history.pop(0)
    
    flow_count = 0
    flow_volume = 0.0

def get_flow_rate():
    """Calculate current flow rate in L/min"""
    global flow_rate_lpm
    # If no flow recently, return 0
    if time.time() - last_pulse_time > 2.0:
        return 0.0
    return flow_rate_lpm

def get_water_usage_history(duration_seconds=None):
    """Get water usage history for a specific time duration"""
    global water_usage_history
    
    if duration_seconds is None:
        return water_usage_history.copy()
    
    current_time = time.time()
    cutoff_time = current_time - duration_seconds
    
    filtered_history = [entry for entry in water_usage_history 
                       if entry['timestamp'] >= cutoff_time]
    
    total_volume = sum(entry['volume'] for entry in filtered_history)
    
    return {
        'entries': filtered_history,
        'total_volume': total_volume,
        'duration_seconds': duration_seconds
    }

def get_daily_water_usage():
    """Get total water usage for today"""
    # Get start of today (midnight)
    today_start = time.mktime(time.localtime()[:3] + (0, 0, 0, 0, 0, 0))
    return get_water_usage_history(duration_seconds=(time.time() - today_start))['total_volume']

def calibrate_flow_sensor(known_volume_liters):
    """
    Calibrate the flow sensor using a known volume of water.
    Run this function with a measured amount of water (e.g., 1 liter)
    to adjust the calibration factor for accuracy.
    
    IMPLEMENTED BY: Tariq Shahmeer (20297244)
    """
    global flow_calibration_factor, flow_count
    
    print("=" * 50)
    print("FLOW SENSOR CALIBRATION MODE")
    print(f"Calibrating with {known_volume_liters} liters...")
    print("Press ENTER to start, then run exactly that amount of water through the sensor.")
    print("=" * 50)
    
    input("Press ENTER when ready to start calibration...")
    
    # Reset counter
    start_count = flow_count
    print("Counting pulses... Press ENTER when done.")
    input("Press ENTER to finish calibration...")
    
    end_count = flow_count
    pulses_received = end_count - start_count
    
    if pulses_received > 0:
        # Calculate new calibration factor
        new_factor = pulses_received / known_volume_liters
        print(f"\nCalibration Results:")
        print(f"  Pulses received: {pulses_received}")
        print(f"  Known volume: {known_volume_liters} L")
        print(f"  Old calibration factor: {flow_calibration_factor} pulses/L")
        print(f"  New calibration factor: {new_factor} pulses/L")
        
        # Ask user if they want to apply
        confirm = input("\nApply new calibration factor? (y/n): ").lower()
        if confirm == 'y':
            flow_calibration_factor = new_factor
            print(f"Calibration factor updated to: {flow_calibration_factor}")
            # Optionally save to config file
            save_calibration_config()
        else:
            print("Calibration cancelled. Using existing factor.")
    else:
        print("No pulses detected. Check sensor connection and water flow.")

def save_calibration_config():
    """Save calibration settings to a config file"""
    config = {
        'calibration_factor': flow_calibration_factor,
        'last_calibration': time.time(),
        'calibrated_by': 'Tariq Shahmeer (20297244)'
    }
    try:
        with open('flow_calibration.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("Calibration settings saved.")
    except Exception as e:
        print(f"Error saving calibration: {e}")

def load_calibration_config():
    """Load calibration settings from config file"""
    global flow_calibration_factor
    try:
        with open('flow_calibration.json', 'r') as f:
            config = json.load(f)
            flow_calibration_factor = config.get('calibration_factor', 450.0)
            print(f"Loaded calibration factor: {flow_calibration_factor}")
    except FileNotFoundError:
        print("No calibration file found. Using default factor.")
    except Exception as e:
        print(f"Error loading calibration: {e}")

# ------------------------ LED Control Functions ---------------------------
def set_led(color, state):
    """Control LEDs: color can be 'red', 'green', 'blue', or 'off'"""
    if color == 'red':
        gp.output(LED_RED_PIN, state)
    elif color == 'green':
        gp.output(LED_GREEN_PIN, state)
    elif color == 'blue':
        gp.output(LED_BLUE_PIN, state)
    elif color == 'off':
        gp.output(LED_RED_PIN, 0)
        gp.output(LED_GREEN_PIN, 0)
        gp.output(LED_BLUE_PIN, 0)

def led_blink(color, duration, interval=0.2):
    """Blink LED for specified duration"""
    end_time = time.time() + duration
    while time.time() < end_time:
        set_led(color, 1)
        time.sleep(interval)
        set_led(color, 0)
        time.sleep(interval)

# ------------------------ Buzzer Functions ---------------------------
def buzzer_beep(duration, frequency=1000):
    """Beep buzzer for specified duration"""
    pi.write(BUZZER_PIN, 1)
    time.sleep(duration)
    pi.write(BUZZER_PIN, 0)

def buzzer_beep_pattern(pattern, beep_duration=0.1, pause_duration=0.1):
    """Beep in pattern: pattern is number of beeps"""
    for i in range(pattern):
        pi.write(BUZZER_PIN, 1)
        time.sleep(beep_duration)
        pi.write(BUZZER_PIN, 0)
        if i < pattern - 1:
            time.sleep(pause_duration)

# ------------------------ Notification Functions ---------------------------
def notification_sequence(sequence_type):
    """Provide notification sequences for different events"""
    if sequence_type == "warning":
        # 3 quick beeps
        buzzer_beep_pattern(3, 0.1, 0.1)
        led_blink('red', 0.5, 0.1)
    elif sequence_type == "start":
        # Single short beep
        buzzer_beep(0.2)
        set_led('green', 1)
        time.sleep(0.2)
        set_led('green', 0)
    elif sequence_type == "end":
        # Long beep
        buzzer_beep(0.5)
        led_blink('blue', 1, 0.3)
    elif sequence_type == "countdown":
        # Short beep
        buzzer_beep(0.1)
        set_led('red', 1)
        time.sleep(0.1)
        set_led('red', 0)

def countdown_notification(seconds_remaining):
    """Provide notification at specific countdown times"""
    if seconds_remaining <= 3 and seconds_remaining > 0:
        # Last 3 seconds: beep and red LED flash
        notification_sequence("countdown")
        return True
    elif seconds_remaining == 10:
        # 10 seconds warning
        notification_sequence("warning")
        return True
    elif seconds_remaining == 5:
        # 5 seconds warning
        notification_sequence("warning")
        return True
    return False

# ------------------------ API Interface Functions (Extended) ---------------------------
# Water usage API endpoints for Flask server integration
# IMPLEMENTED BY: Tariq Shahmeer (20297244)

def api_get_water_usage():
    """API function to get current water usage data"""
    return {
        "total_liters": get_water_usage(),
        "flow_rate_lpm": get_flow_rate(),
        "count": flow_count,
        "calibration_factor": flow_calibration_factor
    }

def api_get_water_status():
    """API function to get current tap water status"""
    return {
        "tap_on": tap_on,
        "water_flowing": tap_on and get_flow_rate() > 0,
        "current_flow_rate_lpm": get_flow_rate(),
        "total_used_liters": get_water_usage()
    }

def api_get_daily_usage():
    """API function to get today's water usage"""
    return {
        "daily_liters": get_daily_water_usage(),
        "date": time.strftime("%Y-%m-%d")
    }

def api_reset_water_usage():
    """API function to reset water usage counter"""
    reset_water_usage()
    return {"status": "success", "message": "Water usage reset"}

def api_calibrate_sensor(known_volume_liters):
    """API function to calibrate flow sensor"""
    try:
        calibrate_flow_sensor(float(known_volume_liters))
        return {
            "status": "success", 
            "message": f"Calibration completed",
            "new_calibration_factor": flow_calibration_factor
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ------------------------ Mode Functions ---------------------------
def routine_mode():
    """Routine mode: brushing teeth, cleaning mouth, washing face"""
    global mode_active, mode_stop_event, tap_on
    
    mode_active = True
    print("=" * 50)
    print("ROUTINE MODE STARTED")
    print("=" * 50)
    
    try:
        # Phase 1: Wet toothbrush (2 seconds water)
        print("[Phase 1/5] Wetting toothbrush...")
        notification_sequence("start")
        set_led('blue', 1)
        pi.write(VALVE_PIN, 1)
        tap_on = True
        
        for remaining in range(2, 0, -1):
            if mode_stop_event.is_set():
                return
            print(f"  Wetting: {remaining}...")
            time.sleep(1)
        
        pi.write(VALVE_PIN, 0)
        tap_on = False
        print("[Phase 1/5] Complete. Brush teeth for 30 seconds")
        
        # Phase 2: Brush teeth (30 seconds no water)
        for remaining in range(30, 0, -1):
            if mode_stop_event.is_set():
                return
            if remaining <= 10:
                print(f"  Brushing: {remaining} seconds remaining...")
                countdown_notification(remaining)
            time.sleep(1)
        
        # Phase 3: Rinse mouth and wet face (40 seconds water)
        print("[Phase 3/5] Rinsing mouth and wetting face...")
        notification_sequence("start")
        set_led('blue', 1)
        pi.write(VALVE_PIN, 1)
        tap_on = True
        
        for remaining in range(40, 0, -1):
            if mode_stop_event.is_set():
                pi.write(VALVE_PIN, 0)
                tap_on = False
                return
            print(f"  Rinsing: {remaining} seconds remaining...")
            countdown_notification(remaining)
            time.sleep(1)
        
        pi.write(VALVE_PIN, 0)
        tap_on = False
        
        # Phase 4: Wash face (60 seconds water)
        print("[Phase 4/5] Washing face...")
        notification_sequence("start")
        set_led('green', 1)
        pi.write(VALVE_PIN, 1)
        tap_on = True
        
        for remaining in range(60, 0, -1):
            if mode_stop_event.is_set():
                pi.write(VALVE_PIN, 0)
                tap_on = False
                return
            print(f"  Face wash: {remaining} seconds remaining...")
            countdown_notification(remaining)
            time.sleep(1)
        
        pi.write(VALVE_PIN, 0)
        tap_on = False
        
        # Phase 5: Cleanup (60 seconds no water)
        print("[Phase 5/5] Cleanup time - Tidy up the area...")
        set_led('green', 1)
        for remaining in range(60, 0, -1):
            if mode_stop_event.is_set():
                return
            if remaining <= 10:
                print(f"  Cleanup: {remaining} seconds remaining...")
            time.sleep(1)
        
        print("=" * 50)
        print("ROUTINE MODE COMPLETE!")
        print("=" * 50)
        notification_sequence("end")
        
    finally:
        pi.write(VALVE_PIN, 0)
        tap_on = False
        set_led('off')
        mode_active = False

def wash_mode():
    """Wash mode: Wet hands, pause for soap, rinse"""
    global mode_active, mode_stop_event, tap_on
    
    mode_active = True
    print("=" * 50)
    print("WASH MODE STARTED")
    print("=" * 50)
    
    try:
        # Phase 1: Wet hands (3 seconds)
        print("[Phase 1/3] Wetting hands...")
        notification_sequence("start")
        set_led('blue', 1)
        pi.write(VALVE_PIN, 1)
        tap_on = True
        
        for remaining in range(3, 0, -1):
            if mode_stop_event.is_set():
                return
            print(f"  Wetting: {remaining}...")
            time.sleep(1)
        
        pi.write(VALVE_PIN, 0)
        tap_on = False
        
        # Phase 2: Soap time (20 seconds pause with notifications)
        print("[Phase 2/3] Apply soap - Water will restart in 20 seconds")
        set_led('green', 1)
        for remaining in range(20, 0, -1):
            if mode_stop_event.is_set():
                return
            if remaining <= 10:
                print(f"  Water starting in {remaining} seconds...")
                countdown_notification(remaining)
            time.sleep(1)
        
        # Phase 3: Rinse hands (30 seconds water)
        print("[Phase 3/3] Rinsing hands...")
        notification_sequence("start")
        set_led('green', 1)
        pi.write(VALVE_PIN, 1)
        tap_on = True
        
        for remaining in range(30, 0, -1):
            if mode_stop_event.is_set():
                pi.write(VALVE_PIN, 0)
                tap_on = False
                return
            print(f"  Rinsing: {remaining} seconds remaining...")
            countdown_notification(remaining)
            time.sleep(1)
        
        pi.write(VALVE_PIN, 0)
        tap_on = False
        
        print("=" * 50)
        print("WASH MODE COMPLETE!")
        print("=" * 50)
        notification_sequence("end")
        
    finally:
        pi.write(VALVE_PIN, 0)
        tap_on = False
        set_led('off')
        mode_active = False

def custom_mode(mode_name):
    """Execute custom mode with user-defined settings"""
    global mode_active, mode_stop_event, tap_on
    
    if mode_name not in custom_modes:
        print(f"Custom mode '{mode_name}' not found")
        return
    
    mode_active = True
    settings = custom_modes[mode_name]
    duration = settings['duration']
    
    print("=" * 50)
    print(f"CUSTOM MODE: {settings['name']}")
    print(f"Duration: {duration} seconds")
    print("=" * 50)
    
    try:
        notification_sequence("start")
        set_led('blue', 1)
        pi.write(VALVE_PIN, 1)
        tap_on = True
        
        # Countdown with notifications
        for remaining in range(duration, 0, -1):
            if mode_stop_event.is_set():
                pi.write(VALVE_PIN, 0)
                tap_on = False
                return
            print(f"  {remaining} seconds remaining...")
            countdown_notification(remaining)
            time.sleep(1)
        
        pi.write(VALVE_PIN, 0)
        tap_on = False
        print(f"=" * 50)
        print(f"CUSTOM MODE '{settings['name']}' COMPLETE!")
        print("=" * 50)
        notification_sequence("end")
        
    finally:
        pi.write(VALVE_PIN, 0)
        tap_on = False
        set_led('off')
        mode_active = False

# ------------------------ Custom Mode Management ---------------------------
def load_custom_modes():
    """Load custom modes from file"""
    global custom_modes
    if os.path.exists(CUSTOM_MODES_FILE):
        try:
            with open(CUSTOM_MODES_FILE, 'r') as f:
                custom_modes = json.load(f)
            print(f"Loaded {len(custom_modes)} custom modes")
        except Exception as e:
            print(f"Error loading custom modes: {e}")
            custom_modes = {}
    else:
        custom_modes = {}
        print("No custom modes file found. Starting fresh.")

def save_custom_modes():
    """Save custom modes to file"""
    try:
        with open(CUSTOM_MODES_FILE, 'w') as f:
            json.dump(custom_modes, f, indent=2)
        print(f"Saved {len(custom_modes)} custom modes")
        return True
    except Exception as e:
        print(f"Error saving custom modes: {e}")
        return False

def add_custom_mode(mode_name, duration):
    """Add or update a custom mode"""
    if mode_name in custom_modes:
        print(f"Updating mode '{mode_name}'")
    else:
        print(f"Adding new mode '{mode_name}'")
    
    custom_modes[mode_name] = {
        'name': mode_name,
        'duration': int(duration),
        'created': time.time()
    }
    save_custom_modes()
    return True

def delete_custom_mode(mode_name):
    """Delete a custom mode"""
    if mode_name in custom_modes:
        del custom_modes[mode_name]
        save_custom_modes()
        print(f"Deleted mode '{mode_name}'")
        return True
    return False

def list_custom_modes():
    """List all saved custom modes"""
    if not custom_modes:
        print("No custom modes saved")
        return []
    return list(custom_modes.keys())

# ------------------------ Main Control Functions ---------------------------
def start_mode(mode):
    """Start a specific mode"""
    global current_mode, mode_active, mode_thread, mode_stop_event
    
    if mode_active:
        print(f"Cannot start {mode}: Another mode is already running")
        return False
    
    if lock_enabled:
        print("Cannot start mode: Tap is locked")
        return False
    
    mode_stop_event.clear()
    
    if mode == "routine":
        current_mode = "routine"
        mode_thread = threading.Thread(target=routine_mode)
    elif mode == "wash":
        current_mode = "wash"
        mode_thread = threading.Thread(target=wash_mode)
    elif mode in custom_modes:
        current_mode = "custom"
        mode_thread = threading.Thread(target=custom_mode, args=(mode,))
    else:
        print(f"Unknown mode: {mode}")
        return False
    
    mode_thread.daemon = True
    mode_thread.start()
    return True

def stop_current_mode():
    """Stop the currently running mode"""
    global mode_active, mode_stop_event
    if mode_active:
        print("Stopping current mode...")
        mode_stop_event.set()
        if mode_thread:
            mode_thread.join(timeout=2)
        pi.write(VALVE_PIN, 0)
        set_led('off')
        mode_active = False
        return True
    return False

def toggle_lock():
    """Toggle lock mode"""
    global lock_enabled
    lock_enabled = not lock_enabled
    if lock_enabled:
        print("🔒 Lock mode: ENABLED - Tap is locked")
        set_led('red', 1)
        if tap_on:
            pi.write(VALVE_PIN, 0)
            global tap_on
            tap_on = False
    else:
        print("🔓 Lock mode: DISABLED - Tap unlocked")
        set_led('off')
    return lock_enabled

def handle_ir_detection():
    """Handle IR sensor detection (basic on/off when not in a mode)"""
    global tap_on
    
    if mode_active:
        # In mode, don't respond to IR
        return
    if lock_enabled:
        # Locked, don't respond
        return
    
    # Check IR sensor (active low: 0 when detected)
    if gp.input(IR_SENSOR_PIN) == 0:  # detected
        if not tap_on:
            tap_on = True
            pi.write(VALVE_PIN, 1)
            print("👋 IR: Tap turned ON")
    else:  # not detected
        if tap_on:
            tap_on = False
            pi.write(VALVE_PIN, 0)
            print("👋 IR: Tap turned OFF")

# ------------------------ API Interface Functions ---------------------------
def api_set_mode(mode_name):
    """API function to set/start a mode"""
    if lock_enabled and mode_name != "lock":
        return {"status": "error", "message": "Tap is locked"}
    success = start_mode(mode_name)
    if success:
        return {"status": "success", "message": f"Mode {mode_name} started"}
    else:
        return {"status": "error", "message": f"Cannot start mode {mode_name}"}

def api_stop_mode():
    """API function to stop current mode"""
    success = stop_current_mode()
    if success:
        return {"status": "success", "message": "Mode stopped"}
    return {"status": "info", "message": "No mode running"}

def api_toggle_lock():
    """API function to toggle lock mode"""
    locked = toggle_lock()
    return {"status": "success", "message": f"Lock mode {'enabled' if locked else 'disabled'}"}

def api_add_custom_mode(name, duration):
    """API function to add a custom mode"""
    try:
        duration = int(duration)
        if duration <= 0:
            return {"status": "error", "message": "Duration must be positive"}
        if duration > 3600:
            return {"status": "error", "message": "Duration cannot exceed 1 hour"}
        success = add_custom_mode(name, duration)
        if success:
            return {"status": "success", "message": f"Custom mode '{name}' added with {duration}s"}
    except ValueError:
        return {"status": "error", "message": "Duration must be a number"}
    return {"status": "error", "message": "Failed to add custom mode"}

def api_delete_custom_mode(name):
    """API function to delete a custom mode"""
    success = delete_custom_mode(name)
    if success:
        return {"status": "success", "message": f"Custom mode '{name}' deleted"}
    return {"status": "error", "message": f"Mode '{name}' not found"}

def api_list_modes():
    """API function to list all available modes"""
    available_modes = {
        "built_in": ["routine", "wash"],
        "custom": list_custom_modes(),
        "current_mode": current_mode,
        "mode_active": mode_active,
        "lock_enabled": lock_enabled,
        "water_usage_liters": get_water_usage()
    }
    return available_modes

def api_ir_status():
    """Get IR sensor status"""
    detected = gp.input(IR_SENSOR_PIN) == 0
    return {
        "ir_detected": detected, 
        "tap_on": tap_on, 
        "lock_enabled": lock_enabled,
        "mode_active": mode_active,
        "current_mode": current_mode
    }

def api_water_usage():
    """Get water usage data - Extended by Tariq Shahmeer (20297244)"""
    return {
        "total_liters": get_water_usage(),
        "flow_rate_lpm": get_flow_rate(),
        "count": flow_count,
        "calibration_factor": flow_calibration_factor,
        "daily_liters": get_daily_water_usage()
    }

def api_reset_water_usage():
    """Reset water usage counter"""
    reset_water_usage()
    return {"status": "success", "message": "Water usage reset"}

# ------------------------ Flask Server for API ---------------------------
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/api/mode/start', methods=['POST'])
    def start_mode_route():
        data = request.json
        mode = data.get('mode')
        return jsonify(api_set_mode(mode))
    
    @app.route('/api/mode/stop', methods=['POST'])
    def stop_mode_route():
        return jsonify(api_stop_mode())
    
    @app.route('/api/lock/toggle', methods=['POST'])
    def toggle_lock_route():
        return jsonify(api_toggle_lock())
    
    @app.route('/api/custom/add', methods=['POST'])
    def add_custom_route():
        data = request.json
        name = data.get('name')
        duration = data.get('duration')
        return jsonify(api_add_custom_mode(name, duration))
    
    @app.route('/api/custom/delete', methods=['POST'])
    def delete_custom_route():
        data = request.json
        name = data.get('name')
        return jsonify(api_delete_custom_mode(name))
    
    @app.route('/api/modes/list', methods=['GET'])
    def list_modes_route():
        return jsonify(api_list_modes())
    
    @app.route('/api/ir/status', methods=['GET'])
    def ir_status_route():
        return jsonify(api_ir_status())
    
    @app.route('/api/water/usage', methods=['GET'])
    def water_usage_route():
        return jsonify(api_water_usage())
    
    @app.route('/api/water/reset', methods=['POST'])
    def water_reset_route():
        return jsonify(api_reset_water_usage())
    
    @app.route('/api/status', methods=['GET'])
    def full_status_route():
        return jsonify({
            **api_ir_status(),
            **api_water_usage(),
            "custom_modes": list_custom_modes()
        })
    
    def run_flask():
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
    FLASK_AVAILABLE = True
    
except ImportError:
    print("⚠️ Flask not installed. API server will not start.")
    print("Install with: pip install flask flask-cors")
    FLASK_AVAILABLE = False
    def run_flask():
        pass

# ------------------------ Main Program ---------------------------
def main():
    """Main program entry point"""
    global pi
    
    print("\n" + "=" * 60)
    print("🚰 AuraFlow Smart Tap System")
    print("   Water Flow Sensor Implementation by Tariq Shahmeer (20297244)")
    print("=" * 60)
    print("Initializing hardware...")
    
    # Initialize pigpio
    pi = pigpio.pi()
    if not pi.connected:
        print("❌ Failed to connect to pigpio daemon")
        print("   Run: sudo pigpiod")
        return
    
    # Initialize GPIO for RPi.GPIO (for IR and LEDs)
    gp.setmode(gp.BOARD)
    gp.setup(IR_SENSOR_PIN, gp.IN, pull_up_down=gp.PUD_UP)
    gp.setup(LED_RED_PIN, gp.OUT)
    gp.setup(LED_GREEN_PIN, gp.OUT)
    gp.setup(LED_BLUE_PIN, gp.OUT)
    
    # Initialize pigpio pins
    pi.set_mode(FLOW_SENSOR_PIN, pigpio.INPUT)
    pi.set_pull_up_down(FLOW_SENSOR_PIN, pigpio.PUD_UP)
    pi.set_mode(VALVE_PIN, pigpio.OUTPUT)
    pi.set_mode(BUZZER_PIN, pigpio.OUTPUT)
    
    # Set initial states
    pi.write(VALVE_PIN, 0)
    pi.write(BUZZER_PIN, 0)
    
    # Setup flow sensor callback
    pi.callback(FLOW_SENSOR_PIN, pigpio.FALLING_EDGE, flow_callback)
    
    # Load calibration settings
    load_calibration_config()
    
    # Load custom modes
    load_custom_modes()
    
    # Start Flask server in background thread
    if FLASK_AVAILABLE:
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        print("\n🌐 API Server started on http://0.0.0.0:5000")
    else:
        print("\n⚠️ API Server not available")
    
    # Display available commands
    print("\n📱 Available API Endpoints:")
    print("   POST /api/mode/start   {'mode': 'routine'}")
    print("   POST /api/mode/start   {'mode': 'wash'}")
    print("   POST /api/mode/start   {'mode': 'Dish Washing'}")
    print("   POST /api/mode/stop")
    print("   POST /api/lock/toggle")
    print("   POST /api/custom/add   {'name': 'Dish Washing', 'duration': 120}")
    print("   POST /api/custom/delete {'name': 'Dish Washing'}")
    print("   GET  /api/modes/list")
    print("   GET  /api/ir/status")
    print("   GET  /api/water/usage")
    print("   GET  /api/status")
    
    print("\n🔧 Hardware Status:")
    print(f"   Flow Sensor: GPIO {FLOW_SENSOR_PIN} (Pin 8)")
    print(f"   IR Sensor: GPIO {IR_SENSOR_PIN} (Pin 3)")
    print(f"   Valve: GPIO {VALVE_PIN} (Pin 10)")
    print(f"   Buzzer: GPIO {BUZZER_PIN} (Pin 12)")
    print(f"   LEDs: Red={LED_RED_PIN}, Green={LED_GREEN_PIN}, Blue={LED_BLUE_PIN}")
    
    print("\n💧 Flow Sensor Status:")
    print(f"   Calibration Factor: {flow_calibration_factor} pulses/L")
    print(f"   Current Flow Rate: 0.00 L/min")
    print(f"   Total Usage: 0.00 L")
    
    print("\n" + "=" * 60)
    print("✅ AuraFlow Smart Tap Ready!")
    print("   Water flow tracking active - Tariq Shahmeer (20297244)")
    print("Press Ctrl+C to exit")
    print("=" * 60 + "\n")
    
    # Main loop for IR detection and flow rate display
    last_display_time = time.time()
    try:
        while True:
            handle_ir_detection()
            
            # Update flow rate display every second
            current_time = time.time()
            if current_time - last_display_time >= 1.0:
                flow_rate = get_flow_rate()
                total_usage = get_water_usage()
                print(f"\r💧 Flow: {flow_rate:.2f} L/min | Total: {total_usage:.2f} L", end="", flush=True)
                last_display_time = current_time
            
            time.sleep(0.05)  # 20Hz refresh rate
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down AuraFlow...")
        
    finally:
        # Cleanup
        pi.write(VALVE_PIN, 0)
        pi.write(BUZZER_PIN, 0)
        set_led('off')
        pi.stop()
        gp.cleanup()
        print("✅ AuraFlow Smart Tap stopped.")
        print("   Final water usage recorded.")
        print(f"   Total water used: {get_water_usage():.2f} liters")

if __name__ == "__main__":
    main()
