PI-MINDER
By Jaspreet Singh

I. Summary

This project is designed to use a Raspberry Pi connected to the internet and a sense-hat module. The program
syncs with your google calandar account upon first start. Any events in the next four days are registered. The first
event is then compared to various thresholds to display a color on the sense-hat 8x8 led matrix. After flashing the
 color, it also flashes the number of event in the said time frame. The check is made every 15 minutes. 

*NOTE: All times can be changed in code to desirable time frame, written in minutes. 

II. Setup

To begin running this project, a sense-hat module must be attached. There is also the need for internet 
connection. The only file not provided in this project is a .json file which must be obtained by setting up a
project on console.developers.google.com with google calandar api. Assign a name of choice which will be shown when
the user needs to login to their google account. Download the .json file to the project directory and rename to
client_secret.json The project should be ready to run at this point.

III. Neccessary Modules

    For the proper execution of this project you will need to use pip to install the following:
	-sense_hat 
	-google-api-python-client
	-python-dateutil
	-oauth2client
	-httplib2

IV. Execution

*NOTE: 'sudo python remind.py' should be used to run the program

At first start, python will either open a browser that lets the user login. If not, copy thelink into browser
of choice and login form there. An alpha-numeric code is provided which must be pasted into the terminal. 

*NOTE: This is only required on first login attempt. 

    Congrats, you now have a working sense-hat alert system! The color codes are as follows:

	-no led flash with BLUE activity LED = system working, no event found in next 4 days
	-GREEN flash with GREEN activity LED = closest event found between 2.5 and 4 days
	-YELLOW flash with YELLOW activity LED = closest event found between 2.5 and 1 days
	-RED flash with RED activity LED = closest event found in next 24 hours
    
V. Acknowledgements

This project was adapted from MAKEZINE's project by John M Wargo which was designed for Pimoroni Unicorn Hat.
The code was changed to work for SenseHat and was repurposed to be used for events such homework assignments or 
project deadlines which is a longer time frame than the MAKE project was intended to work for. 
