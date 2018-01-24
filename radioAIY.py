#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a recognizer using the Google Assistant Library with button support.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

The Google Assistant Library can be installed with:
    env/bin/pip install google-assistant-library==0.0.2

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import sys
import threading
import sys
import time
import os

import aiy.assistant.auth_helpers
import aiy.voicehat
from google.assistant.library import Assistant
from google.assistant.library.event import EventType

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


class MyAssistant(object):
    """An assistant that runs in the background.

    The Google Assistant Library event loop blocks the running thread entirely.
    To support the button trigger, we need to run the event loop in a separate
    thread. Otherwise, the on_button_pressed() method will never get a chance to
    be invoked.
    """
    station = 0
    pause = 0
    playing = 0
    volume = 0
    st = (
          {'n':'RFI','ad':'http://live02.rfi.fr/rfimonde-96k.mp3'},
          {'n':'France culture','ad':'http://direct.franceculture.fr/live/franceculture-midfi.mp3'},
          {'n':'FIP','ad':'http://direct.fipradio.fr/live/fip-midfi.mp3'},
          {'n':'RMC','ad':'http://rmc.bfmtv.com/rmcinfo-mp3'},
          {'n':'RTL','ad':'http://streaming.radio.rtl.fr/rtl-1-44-96'},
          {'n':'France info','ad':'http://direct.franceinfo.fr/live/franceinfo-midfi.mp3'},
          {'n':'radio classique','ad':'http://broadcast.infomaniak.net:80/radioclassique-high.mp3'},
          {'n':'France musique','ad':'http://direct.francemusique.fr/live/francemusique-midfi.mp3'},
          {'n':'jazz radio','ad':'http://broadcast.infomaniak.net:80/jazzradio-high.mp3'},
          {'n':'Europe 1','ad':'http://mp3lg3.scdn.arkena.com/10489/europe1.mp3'},
          {'n':'sud radio','ad':'http://broadcast.infomaniak.ch/start-sud-high.mp3'},
          {'n':'France inter','ad':'http://direct.franceinter.fr/live/franceinter-midfi.mp3'},
          {'n':'frequence jazz','ad':'http://broadcast.infomaniak.ch/frequencejazz-high.mp3'},
          {'n':'Latina','ad':'http://broadcast.infomaniak.net/start-latina-high.mp3'},
          {'n':'le Mouv','ad':'http://direct.mouv.fr/live/mouv-midfi.mp3'},
          {'n':'Euro News','ad':'http://euronews-01.ice.infomaniak.ch/euronews-01.aac'},
          {'n':'radio grenouille','ad':'http://live.radiogrenouille.com/live'}
          )





    def __init__(self):
        self._task = threading.Thread(target=self._run_task)
        self._can_start_conversation = False
        self._assistant = None

    def start(self):
        """Starts the assistant.

        Starts the assistant event loop and begin processing events.
        """
        self._task.start()

    def _run_task(self):
      
        os.system('touch stFile')
        f = open('stFile','r+')
        stStr = f.read(10)
        f.close()
        if (len(stStr)==0):
         self.station = 0
        else:
         self.station = int(stStr)

        print('==>',stStr,self.station)

        self.pause = 0
        self.playing = 0
        self.volume = 70
 
        os.system("amixer set 'Master' 70%")

        credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
        with Assistant(credentials) as assistant:
            self._assistant = assistant
            for event in assistant.start():
                self._process_event(event)

    def radioOn(self):
  
        print('radioOn1')
        print(self.station)
        b = 'echo '+str(self.station)+' >stFile'
        os.system(b)
        if(self.playing == 1):os.system('kill -9 `ps -C vlc -o pid=`')
        aiy.audio.say(self.st[self.station]['n'])
        self.playing = 1
        os.system('cvlc --gain=1 '+self.st[self.station]['ad']+'&')   
        return

    def _process_event(self, event):
      
       status_ui = aiy.voicehat.get_status_ui()
       if event.type == EventType.ON_START_FINISHED:
            status_ui.status('ready')
            self._can_start_conversation = True
            # Start the voicehat button trigger.
            aiy.voicehat.get_button().on_press(self._on_button_pressed)
            if sys.stdout.isatty():
                print('Say "OK, Google" or press the button, then speak. '
                      'Press Ctrl+C to quit...')

       elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')
        os.system("amixer set 'Master' 0%")
        self._can_start_conversation = False

       elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
            print('You said:', event.args['text'])
            text = event.args['text'].lower()         
            time.sleep(0.1) 
            os.system("amixer set 'Master' " + str(self.volume) + "%")
   
            if ('play' in text) or ('resume' in text):
                self._assistant.stop_conversation()                
                self.radioOn()
                status_ui.status('ready')
        
            elif 'stop' in text: 
                self._assistant.stop_conversation()                
                if(self.playing==1): os.system('kill -9 `ps -C vlc -o pid=`')
                self.playing = 0
                status_ui.status('ready')
                aiy.audio.say('see you soon...')
               
            elif 'pause' in text:
                self._assistant.stop_conversation() 
                if(self.playing==1): os.system('kill -9 `ps -C vlc -o pid=`')
                self.playing = 0
                status_ui.status('ready')

            elif 'volume' in text:
                self._assistant.stop_conversation() 
                if 'up' in text:self.volume+=10
                elif 'down' in text : self.volume-=10
                elif ('one' in text)or('1' in text): self.volume=10
                elif ('two' in text)or('2' in text): self.volume=20
                elif ('three' in text)or('3' in text): self.volume=30
                elif ('four' in text)or('4' in text):self.volume=40
                elif ('five' in text)or('5' in text):self.volume=50
                elif ('six' in text)or('6' in text):self.volume=60
                elif ('seven' in text)or('7' in text):self.volume=70
                elif ('eight' in text)or('8' in text):self.volume=80
                elif ('nine' in text)or('9' in text):self.volume=90
                elif ('ten' in text)or('10' in text):self.volume=100
                if(self.volume>100):self.volume=100
                if(self.volume<0):self.volume=0
                t= "amixer set 'Master' "+str(self.volume)+"%"
                os.system(t)
                status_ui.status('ready')
   
    
            elif 'radio' in text.lower():
                self._assistant.stop_conversation()
                if 'next' in text:self.station+=1
                elif 'previous' in text:self.station-=1
                elif ('one' in text) or('1' in text):self.station=0
                elif ('two' in text) or ('2' in text):self.station=1
                elif ('three' in text) or ('3' in text):self.station=2
                elif ('four' in text) or ('4' in text):self.station=3
                elif ('five' in text) or ('5' in text):self.station=4
                elif ('six' in text) or ('6' in text):self.station=5
                elif ('seven' in text) or ('7' in text):self.station=6
                elif ('eight' in text) or ('8' in text):self.station=7
                elif ('nine' in text) or ('9' in text):self.station=8
                elif ('ten' in text) or ('10' in text):self.station=9
                if(self.station >= len(self.st)): self.station = 0
                if(self.station <0): self.station = len(self.st)-1
                self.radioOn()
                status_ui.status('ready') 
        

            else:       
                  for s in range(len(self.st)):
                     if self.st[s]['n'].lower() in text.lower():
                          self._assistant.stop_conversation() 
                          self.station = s
                          self.radioOn()
                          status_ui.status('ready')


       elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

       elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        print('ok')
        status_ui.status('ready')
        self._can_start_conversation = True
       elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)



    def _on_button_pressed(self):
        # Check if we can start a conversation. 'self._can_start_conversation'
        # is False when either:
        # 1. The assistant library is not yet ready; OR
        # 2. The assistant library is already in a conversation.
        if self._can_start_conversation:
            self._assistant.start_conversation()


def main():
    MyAssistant().start()


if __name__ == '__main__':
    main()
