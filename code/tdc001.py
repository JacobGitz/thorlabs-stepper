"""
written by Jacob Lazarchik, summer of 2025
Refer to my PDF of notes for details.
"""

import time
from thorlabs_apt_device import TDC001
from thorlabs_apt_device.enums import EndPoint

#initializing stage globally for easy access
stage = TDC001()
stage.status["homing"]=False
def error_callback(source, msgid, code, notes):
    """Report any controller-level errors."""
    print(f"Device {source} reported error code {code}: {notes!r}")

def wait_for(cond, timeout=10, interval=0.1):
    """
    Block until cond() is True or timeout expires.
    Raises TimeoutError on failure.
    """
    time.sleep(.3)
    start = time.time()
    while not cond():
        print(f"\rRuntime: {time.time()-start}", end="", flush=True)
        if time.time() - start > timeout:
            raise TimeoutError("Timed out waiting for condition")
        time.sleep(interval)
        
    print("done waiting!")

def move_relative(counts):
    print(f"Moving {counts} counts…")
    stage.move_relative(counts)
    wait_for(lambda: not (stage.status["moving_forward"] or stage.status["moving_reverse"]),
             timeout=(4/20000)*counts)
    print("Position after move:", stage.status["position"])

def initialize_without_homing():
    time.sleep(0.5)  # give the background thread a moment to start polling
    #Register error callback
    stage.register_error_callback(error_callback)
    time.sleep(.5)
    stage.identify()
    stage.status["homing"]=False
    stage.stop()
    time.sleep(.5)
    #print out the status of everything afterwards for use
    print("Status after initializing:", stage.status)

def main():

    #set up a connection between controller and system
    initialize_without_homing()

    #prompt user for movements of stepper
    while True:
        resp = input("Enter target position (counts) or 'q' to quit: ").strip()
        if resp.lower() in ("q", "quit", "exit"):
            break

        try:
            target = int(resp)
        except ValueError:
            print("  ❌ Invalid number, try again.")
            continue

        move_relative(target)
    stage.close()
    print("Goodbye!")


main()

