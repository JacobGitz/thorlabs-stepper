"""
written by Jacob Lazarchik, summer of 2025
This script is for initializing many thorlabs TDC001 stepper controllers on a PC
Refer to my PDFs/code for details
Remaining Documentation in thorlabs-apt-device.readthedocs.io website
"""

#all the imports this script needs lol
import time
from serial.tools import list_ports
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
def detect_multi_thorlabs()
-go through all serial ports, list all devices
-identify which serial ports are connected to thorlabs devices
-return thorlabs devices as a list of objects that contain portinfo
-this function is mostly UNIVERSAL for detecting any device with a vendor_id, and is super useful, can be used in future projects
""" 
def detect_multi_thorlabs(vendor_ids=[1027,4883]):
    #pyserial is useful, their website for documentation is https://pyserial.readthedocs.io/en/latest/pyserial.html 
    #I note another option is pyvisa, which is agnostic to the type of communication device and can use gpib,ethernet, everything and isn't messy
    #they also have a git repo for more useful info, https://github.com/pyserial/pyserial/tree/master/serial/tools 
    #this has a main function in the script list_ports.py that returns ListPortInfo objects for each port (a class object, refer to object oriented programming)
    #ListPortInfo objects have parameters: device,name,description,hwid,vid (vendor id), pid (product id), serial_number, location, manufacturer, product, interface 
    #https://pyserial.readthedocs.io/en/latest/tools.html has this information if you need to read up on it
    #print(list_ports.comports()) #this prints out a big list of ListPortInfo objects
    
    device_list = [] #create an empty list to populate with devices that match vendor id

    for port in list_ports.comports():
        #print(port.vid) #useful for repurposing this code for other things, for the TDC001, it returns a vendor id of 1027, which is why I set to default, 4883 is another one that appears, these also may be in hexidecimal (1027 = 0x0403)
        if port.vid in vendor_ids: # https://www.w3schools.com/python/python_lists_access.asp
            device_list.append(port)  #self explanatory
    
    return device_list


"""
main()
    -main method for this file, will be shifted to run if filename==main in the future
    -mostly useful just for debugging this controller, will be controlled by a higher level class in the future 
"""

def main():
    print(detect_multi_thorlabs())
    



    """
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
    """


main() 
 
