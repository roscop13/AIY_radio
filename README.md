# AIY_radio
this is a voice controlled internet radio for raspberry pi based on the raspiaudio.com shield (Google AIY voice kit compatible), I'm the manufactuer of the shield https://www.raspiaudio.com/raspiaudio-ayi and this is an example of project with it, it could be also used with USB audio devices.

Hardware requirement: 
-Raspberry Pi 3
-This shield that includes stereo speakers microphone and more https://www.raspiaudio.com/raspiaudio-ayi or the bulky cardboard thing by Google or you can of course use a usb mic and the onboard audio (low quality for a radio)

Software installation:
-Burn this image Google AIY image  (https://dl.google.com/dl/aiyprojects/vision/aiyprojects-2018-01-03.img.xz)
-Start your raspberry and run the script to install the audio driver and run the command if you are using the Raspiaudio sound card: sudo wget -O - aiy.raspiaudio.com | bash
-Follow the procedure to enable your google credential here, the goal is to get a assistant.json file tht you will copy /home/pi here is the full procedure: https://aiyprojects.withgoogle.com/voice/#users-guide-1-2--turn-on-the-google-assistant-api
-copy the radioAIY.py file into the example directory src/examples/voice/
-run python radioAIY.py

Yon can edit you favorite radios URL, push the red button or say "ok google" before saying the following commands:
"
play
resume
pause

next radio
previous radio
radio 1
...
radio 10

volume up
volume down
volume 1
...
volume 10"

(or directely the name of your radio) :  "RFI, FIP, RMC....

stop"


Credit to Louis Ros
