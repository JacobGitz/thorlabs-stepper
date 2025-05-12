"""
written by Jacob Lazarchik, summer of 2025
This script is for initializing many thorlabs TDC001 stepper controllers on a PC
Refer to my PDFs/code for details
Remaining Documentation in thorlabs-apt-device.readthedocs.io website
"""

#all the imports this script needs lol
import time
from thorlabs_apt_device import TDC001

#initializing stage globally for easy access, setting to none for now, will be changed in the future
stage = None

"""
initialize()
    -recognizes tdc001 controller, prints out existing parameters, flashes led to show it has worked.
    -must be run in main before doing anything else! 
    -fixes the issue of the constructor immediately homing the device, stops this from occuring.
    -still doesn't account for multiple controllers & higher level scripts controlling these devices, will be shifted to OOP
"""
def initialize(homing=False):
    global stage
    #TDC001 constructor takes many params, TDC001(serial_port=None, vid=None, pid=None, manufacturer=None, product=None, serial_number='83', location=None, home=True, invert_direction_logic=True, swap_limit_switches=True)
    if homing==False:
        #this only executes if you don't want homing, refer to aptdevice_motor module at the bottom of the init function to see where this issue occurs
        stage = TDC001(home=False)
        time.sleep(.1)
        stage.set_enabled()
        time.sleep(.1)
    else:
        stage = TDC001()

    time.sleep(0.1)  # give the background thread a moment to start polling
    #Register error callback
    stage.register_error_callback(error_callback)
    time.sleep(.1)
    #flash led on controller if identification successful
    stage.identify()
    time.sleep(.1)
    #print out the status of everything afterwards for use
    print("Status after initializing:", stage.status)
    


"""
error_callback()
    -this should never actually be used unless something goes very wrong
    -copied from the website thorlabs-apt-device.readthedocs.io 
"""

def error_callback(source, msgid, code, notes):
    #Report any controller-level errors.
    print(f"Device {source} reported error code {code}: {notes!r}")

"""
wait_for()
    -a useful function that can wait for any lambda function return to change basically.
    -useful for monitoring if a process has completed before executing something else
    -see an example of how to use this method correctly in move_relative.
    -for more info on lambda functions, check w3schools.com/python
"""

def wait_for(cond, timeout=120, interval=0.1):
    #Block until cond() is True or timeout expires.
    #Raises TimeoutError on failure.
    time.sleep(.3)
    start = time.time()
    while not cond():
        print(f"\rRuntime: {time.time()-start}", end="", flush=True)
        if time.time() - start > timeout:
            stage.close()
            raise TimeoutError("Timed out waiting for condition")
        time.sleep(interval)
    #print("done waiting!") - commented out, but could be useful for debugging 


"""
move_relative()
    -simply moves the attached device relative to the starting point. move_absolute is also supported
    -also waits until the device has officially stopped moving to print the new position
"""
def move_relative(counts):
    print(f"Moving {counts} counts…")
    stage.move_relative(counts)
    wait_for(lambda: not (stage.status["moving_forward"] or stage.status["moving_reverse"]))
    print("Position after move:", stage.status["position"])


"""
main()
    -main method for this file, will be shifted to run if filename==main in the future
    -mostly useful just for debugging this controller, will be controlled by a higher level class in the future 
"""
def main():
    #set up a connection between controller and system
    initialize(homing=False)
    time.sleep(.5)
    #this actually failed to work, in fact, changing the velocity parameters actually does nothing based on my tests???? idk why
    #stage.set_velocity_params(max_velocity=150000,acceleration=100000)
    time.sleep(.2)
    #prompt user for movements of stepper
    while True:
        resp = input("Enter target position (counts) or 'Q' to quit: ").strip()
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

