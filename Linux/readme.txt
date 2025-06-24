For these shell scripts, just open a terminal in this directory and type "bash a-file.sh" (replace with name of file you want to run) and it will boot up. 

You can also make them executable files with the "chmod +x file-name.sh" command. They may already be, so just right click or something and see if it says "run as program"

I didn't test the desktop icon thing, and I just suggest you click no on that. But, it should all work otherwise just fine. 

You may note on Linux these two scripts do not work entirely, this is because the docker compose files are configured to work with  Windows specifically.

Specifically, docker desktop runs in a hypervisor for compatibility, and USB devices must be passed through to the virtual machine for docker containers to use them

There is something called usbip or something in the docker documentation, and several softwares that allow you to provide USB devices to containers

I supplied notes for this on windows in my original stable release, but not for linux. It was *partially incorrectly* discussed in the presentation as well 
