# Agent Codes
### Looking at agent unavailable codes on phones for call center

The purpose of this project is to simplify the process for organizing agent
data in regards to time spent in various codes on phone software.

Agent_Unavailable_Time.py pulls from 4 Excel spreadsheets that are
remotely downloaded from inContact (phone software). It reorganizes the data
into a usable format for our Business Desk.

Export.py exports that data as two separate Excel spreadsheets.

Graphs.py creates visualizations for use by the supervisors and team leads. It
also exports a few small spreadsheets and other data for building the weekly
Agent Time Allocation Report.

### Environment Variables
Set username variable in .env

### Mac-to-Windows (and vice versa) Issues
You may have to change all the file path strings due to the difference in how
Macs and Windows read file paths.
* Mac: Need to use /
* Windows: Need to use \

**Locations:**
* Beginning of Agent_Unavailable_time.py (4)
* End of Graphs.py (3)
* End of Export.py (2)
* Beginning of Emails.py (1)
