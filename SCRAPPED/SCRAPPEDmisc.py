    # # Display available commands
    # print("\n📱 Available API Endpoints:")
    # print("   POST /api/mode/start   {'mode': 'basic'}")
    # print("   POST /api/mode/start   {'mode': 'wash'}")
    # print("   POST /api/mode/start   {'mode': 'Dish Washing'}")
    # print("   POST /api/mode/stop")
    # print("   POST /api/lock/toggle")
    # print("   POST /api/custom/add   {'name': 'Dish Washing', 'duration': 120}")
    # print("   POST /api/custom/delete {'name': 'Dish Washing'}")
    # print("   GET  /api/modes/list")
    # print("   GET  /api/ir/status")
    # print("   GET  /api/water/usage")
    # print("   GET  /api/status")

# def basic_mode():
#     """Regular IR tap functionalitites"""
#     # basic function of when IR detected > valve on, when IR not detected > valve off
#     # use the intermediary boolean variable between them called tap_on, so IR status goes into the
#     # variable and the variable decides if valve is on
#     # and create a global boolean variable of api_tap_on that forces the valve on or off
#     # that when the lock variable is true, make both tap_on and api_tap_on variable always false
