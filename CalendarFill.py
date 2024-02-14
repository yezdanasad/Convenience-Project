# Import useful stuff
from pypdf import PdfReader
import pandas as pd
from tabula import read_pdf
import tabula
import datetime as dt
import os.path


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

dfs = tabula.read_pdf("Path to your table", pages = 'all')# read and parse pdf
dfs = dfs[0]#Assign 'list' object to pandas df
dfs = dfs.dropna().reset_index()#Drop empty rows
dfs = dfs.drop('index', axis = 1)# Drop redundant column
duties_list = dfs.iloc[8].tolist()#Select the row with dads name and duties. and turn it into a list
duties_list = duties_list[1:]# Drop dads name, so its just his duties for the week in order.

#Define some lists to be used later.
dateTimesStart = []
dateTimesEnd = []
start_date = datetime.now()  # Use the current date and time as the starting point
#start_date = start_date + timedelta(days = 2)# Add number of days in case the lit comes in on a sunday and work starts on a monday.
start_time = datetime.strptime("09:00", "%H:%M").time()  # Specify the time of day, for start of duty
start_time_2 = datetime.strptime("20:00", "%H:%M").time() # Same thing as the last line but for end of duty, just so I dont have to set the start and end time to the same time.
# Combine the start date and time
start_datetime = datetime.combine(start_date.date(), start_time)
start_datetime2 = datetime.combine(start_date.date(), start_time_2)
# Generate datetime stamps for the same time each day over the next week
end_datetime = start_datetime + timedelta(days=6)
end_datetime2 = start_datetime2 + timedelta(days=6)
date_range = pd.date_range(start=start_datetime, end=end_datetime, freq='D')
date_range2 = pd.date_range(start=start_datetime2, end=end_datetime2, freq='D')


# Append the resulting datetime stamps to appropriate lists.
for dtt in date_range:
    dts = dtt.strftime('%Y-%m-%d %H:%M:%S')
    dts = dts.replace(' ','T')
    dateTimesStart.append(dts)
for dtt in date_range2:
    dts = dtt.strftime('%Y-%m-%d %H:%M:%S')
    dts = dts.replace(' ','T')
    dateTimesEnd.append(dts)


scopes = ["https://www.googleapis.com/auth/calendar"]#Define scope for the build of the google api

#Function to fill in credientials properly, and run the task-scheduling load.
def main():
    creds = None # Set to none in case of different stuff happening, see lines 74-83
    def update_calendar():
        for i in range(len(duties_list)):
         event = {
         "summary" : duties_list[i],
         "location" : "Darrent Valley Hospital",
         "description" : "Duty For The Day",
         "colorId" : 5,
         "start" : {
             "dateTime" : dateTimesStart[i],
             "timeZone" : "Europe/London"} ,
         "end" : {
             "dateTime" : dateTimesEnd[i],
             "timeZone" : "Europe/London"}
            }# The dictionary gives all the necesary key-value pairs to create a calendar object
         event = service.events().insert(calendarId = "primary", body = event).execute()# Connect to calenadr with api, and add the event
         print(f"Event created !")# Confirms an event was added
    # Conditional statements to deal with creds misbehaving
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("googleapicredentials.json",scopes)
            creds = flow.run_local_server(port = 0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("calendar","v3", credentials = creds)# Running the important functions once the creds have been verified
        update_calendar()

    except HttpError as error:
        print('An error has occured :', error)# Error catch statement, bug to note: will return bad API request if you mess up sthg with the key-value pairs in the event dictionary.

# Condition to run the main() function.        
if __name__ == '__main__':
    main()
