######################### Intro ###################################################################

These scripts automatically boot, build and shutdown the 2 docker containers for this whole project easily on Linux. 

(For Windows, refer to the Windows directory in this repo)

For these shell scripts, just open a terminal in this directory and type "bash a-file.sh" (replace with name of file you want to run) and it will boot up. 

You can also make them executable files with the "chmod +x file-name.sh" command. They may already be, so just right click or something and see if it says "run as program"

######################### Bugs you may encounter ##############################

You may note on Linux and Windows these two containers do not work entirely out of the box (USB devices are not showing up)....

Docker desktop runs in a hypervisor for compatibility, and USB devices must be passed through to the virtual machine for docker containers to use them

There is something called usbipd or something in the docker documentation, and several softwares that allow you to provide USB devices to containers

I supplied notes for this on Windows in my original stable release(main branch readme.md), but not for Linux. It was *partially incorrectly* discussed in the presentation as well. 

But, if you run the frontend on a Linux machine, and then the backend on a separate Windows machine (with usbipd-win or whatever I discussed in readme.md) then it will work successfully. 

(backend first, then frontend, otherwise frontend won't see backend, restart frontend container if you cannot find the proper backend)

Another common issue is that stuff isn't working anymore if you unplug a USB device while these containers are running. Reboot them. 

############## Notes for a Future Person ##################################

For a future person in 2035 or something, this building process *may* fail if you try to do it from scratch in this script. Hopefully, pre-built images from this time (2025) will be stored somewhere and just run those instead. You can build on top of those and edit those internally to get what you like and make revised images from them. 

However, in the case you do not like my code or existing images, you can rebuild from scratch using these scripts. If it nukes itself during this process, chances are it is because it is pulling the base "python 3.13 slim" images in the Dockerfiles from Docker Hub, as well as a bunch of other online dependencies for Ubuntu.

I will try my best to store everything that is a online dependency for the build process in this git repo, but not all of it can be submitted to Github. So, hopefully we have network storage in the lab or a drive which stores this git repo and stores of all the original ubuntu dependencies and the base python image as well. 

If everything goes wrong, contact a guy named Jacob Lazarchik (me) at lazarchik.jacob@gmail.com, maybe spam me a bit or submit a git issue to my repo on github.

(I don't check my email often lol)

