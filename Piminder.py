#!/usr/bin/env python
'''*****************************************************************************************************************
    Piminder
    Google Calendar example code: https://developers.google.com/google-apps/calendar/quickstart/python

********************************************************************************************************************'''
from __future__ import print_function, division, absolute_import

import colorsys
import datetime
import math
import os
import sys
import time

import httplib2
import numpy as np
import oauth2client

from apiclient import discovery
from dateutil import parser
from oauth2client import client
from oauth2client import tools
from sense_hat import SenseHat
try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

sense = SenseHat()
# Google says: If modifying these scopes, delete your previously saved credentials at ~/.credentials/client_secret.json
# On the pi, it's in /root/.credentials/
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Pi Reminder'
CALENDAR_ID = 'primary'
HASH = '#'
HASHES = '################################################'

# Reminder thresholds
FIRST_THRESHOLD = 3600 #2.5 days, WHITE lights before this
# RED for anything less than (and including) the second threshold
SECOND_THRESHOLD = 1440  # 1 day, YELLOW lights before this

# COLORS
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 153, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# constants used in the app to display status
CHECKING_COLOR = BLUE
SUCCESS_COLOR = GREEN
FAILURE_COLOR = RED

def set_activity_light(color, increment):
    # Pi is still running the code. So, it shows GREEN when connecting to Google, then switches to BLUE when
    # its done.
    global current_activity_light
    sense.clear()
    # Indicates the current_activity light
    if current_activity_light >7:
	 # start over at the beginning when you're at the end of the row
         current_activity_light =0
         # increment the current light (to the next one)
         current_activity_light += 1
    # set the pixel color
    sense.set_pixel(current_activity_light, 0, color[0], color[1], color[2])


#Change to hold color 
def flash_all(flash_count, delay, color, num):
    # light all of the LEDs in a RGB single color. Repeat 'flash_count' times
    # keep illuminated for 'delay' value
    for index in range(flash_count):
        for y in range(8):
            for x in range(8):
                sense.set_pixel(x, y, color[0], color[1], color[2])
        
        time.sleep(delay)
        sense.clear()
        time.sleep(delay)
	sense.show_message(num, text_colour = [color[0], color[1], color[2]])
	time.sleep(delay)


def get_credentials():
    # https://developers.google.com/google-apps/calendar/quickstart/python
    global credentials
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        print('Creating', credential_dir)
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'pi_remind.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to', credential_path)
    return credentials

def get_next_event(search_limit):
    # modified from https://developers.google.com/google-apps/calendar/quickstart/python
    # get all of the events on the calendar from now through X minutes from now
    print(datetime.datetime.now(), 'Getting next event')
    # this 'now' is in a different format (UTC)
    now = datetime.datetime.utcnow()
    then = now + datetime.timedelta(minutes=search_limit)
    # turn on a sequential CHECKING_COLOR LED to show that you're requesting data from the Google Calendar API
    set_activity_light(CHECKING_COLOR, True)
    try:
        # ask Google for the calendar entries
        events_result = service.events().list(
            # get all of them between now and X  minutes from now
            calendarId=CALENDAR_ID,
            timeMin=now.isoformat() + 'Z',
            timeMax=then.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime').execute()
	
        # Success
        set_activity_light(SUCCESS_COLOR, False)
        # Get the event list
        event_list = events_result.get('items', [])
	if not event_list:
	    num_events = 0    
	else:
	    num_events = str(len(event_list))
        if not event_list:
            #No upcoming events at all, so nothing to do right now
            print(datetime.datetime.now(), 'No entries returned')
            return None , num_events
        else:
	    current_time = datetime.datetime.now()		  
            # loop through the events in the list
            for event in event_list:
                # Check to see if startTime exists
                start = event['start'].get('dateTime')
               
		 # Return the first event that has a start time
                if start:
                    # Convert the string it into a Python dateTime object 
                    event_start1 = parser.parse(start)  
		    event_start = event_start1.replace(tzinfo=None)       
		    # Only pick events that haven't happened yet
		    if current_time < event_start:
                        #Get name of event
                        event_summary = event['summary'] if 'summary' in event else 'No Title'
                        print('Found event:', event_summary)
                        print('Event starts:', start)
                        # Time to start
                        time_delta = event_start - current_time
                        # Round to the nearest minute and return with the object
                        event['num_minutes'] = time_delta.total_seconds() // 60
                        return event , num_events
    except:
       
        print('Error connecting to calendar:', sys.exc_info()[0], '\n')
        flash_all(1, 2, FAILURE_COLOR,X)
        set_activity_light(FAILURE_COLOR, False)

    return None , 0


def main():
    sense.low_light = True
    # initialize the lastMinute variable to the current time to start
    last_minute = datetime.datetime.now().minute
    # on startup, just use the previous minute as lastMinute
    if last_minute == 0:
        last_minute = 59
    else:
        last_minute -= 1

    # infinite loop to continuously check Google Calendar for future entries
    while 1:
        # get the current minute
        current_minute = datetime.datetime.now().minute
        if current_minute != last_minute:
            # reset last_minute to the current_minute
            last_minute = current_minute
            # get the next calendar event (within the specified time limit [in minutes])
            next_event, count = get_next_event(5760)
            # enters only if event exists
            if next_event is not None:
                num_minutes = next_event['num_minutes']
                if num_minutes != 1:
                    print('Starts in', int(num_minutes), 'minutes\n')
                else:
                    print('Starts in 1.0 minute\n')
               
                if num_minutes >= FIRST_THRESHOLD:
                    # Flash the lights in GREEN
                    flash_all(2, 0.25, GREEN, count)
                    # set the activity light to GREEN as an indicator
                    set_activity_light(GREEN, False)
               
                elif num_minutes > SECOND_THRESHOLD:
                    # Flash the lights YELLOW
                    flash_all(4, 0.25, YELLOW, count)
                    # set the activity light to ORANGE as an indicator
                    set_activity_light(ORANGE, False)
       
                else:
                    flash_all(8,.25,RED, count)
                    set_activity_light(RED, False)
        # wait then check again
        # Time between checks
        time.sleep(600)

    # this should never happen since the above is an infinite loop
    print('Leaving main()')


# now tell the user what we're doing...
print('\n')
print(HASHES)
print(HASH, "  ___  _   __  __  _           _            ",HASH)
print(HASH, " | _ \(_) |  \/  |(_) _ _   __| | ___  _ _  ",HASH)
print(HASH, " |  _/| | | |\/| || || ' \ / _` |/ -_)| '_| ",HASH)
print(HASH, " |_|  |_| |_|  |_||_||_||_|\__,_|\___||_|   ",HASH)
print(HASH, "                                            ",HASH)
print(HASH, "  Made for SenseHat by Jas and kinda Inder  ",HASH)
print(HASHES)                                           


# The app flashes a GREEN light in the first row every time it connects to Google to check the calendar.
current_activity_light = 7 


# Initialize the Google Calendar API stuff
credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

print('\nApplication initialized\n')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
	print('\nClearing LEDs\n')
	sense.clear()
        print('Exiting application\n')
        sys.exit(0)
