import pandas as pd
import datetime as dt
from decimal import Decimal
import os

# Set username from .env
username = os.environ['username']

'''
Import inContact spreadsheets
'''
# Read in Agent Unavailable Time
df_col_names = ['Agent Name', 'Code', 'Code Type', 'Duration',
                'Duration in Seconds', 'Percent']
df = pd.read_excel(fr'\Users\{username}\Downloads\IC_Reports_AgentUnavailableTime.xlsx',
                   names=df_col_names)

# Read in Agent Summary
summary_col_names = ['Agent Name', 'Handled (Inbound)',
                     'Avg Talk Time (Inbound)', 'Handled (Outbound)',
                     'Avg Talk Time (Outbound)', 'Available Time',
                     'Total Unavailable Time', 'Refused', 'Login Time',
                     'Working Rate', 'Occupancy']
summary = pd.read_excel(fr'\Users\{username}\Downloads\IC_Reports_AgentSummary.xlsx',
                        names=summary_col_names)

# Read in Agent List
agentlist_col_names = ['Team Name (ID)', 'Agent Name', 'Last Login',
                       'Skill Count']
agentlist = pd.read_excel(fr'\Users\{username}\Downloads\IC_Reports_AgentList.xlsx',
                          names=agentlist_col_names)

# Read in Supervisor Snapshot
snapshot_col_names = ['Agent Name', 'Inbound Handled', 'Inbound AHT',
                       'Outbound Handled', 'Outbound AHT', 'Available Time',
                       'Unavailable Time', 'Refused', 'Login Time',
                       'Occupancy']
needed_cols = [0, 2, 6, 8, 9, 13, 14, 21, 23, 29]
snapshot = pd.read_excel(fr'\Users\{username}\Downloads\Supervisor Snapshot.xlsx',
                         names=snapshot_col_names, skiprows=11,
                         usecols=needed_cols)

# The process below removes all but the first section of the dataframe
# Create boolean series regarding null values for name
nullname = snapshot['Agent Name'].isnull()

# Find the number of rows in first dataframe (before first null value)
def boundary_maker(series):
    new_list = []
    for i in series:
        if i == False:
            new_list.append(i)
        else:
            break
    return new_list

# Drop all rows that are not in first section of dataframe
non_null_list = boundary_maker(nullname)
needed_rows = len(non_null_list)
snapshot = snapshot[0:needed_rows]

'''
Some basic cleaning
'''
# Remove irrelevant columns
df = df.drop(columns=['Code Type','Percent'])

# Assign agent name to all applicable rows
df['Agent Name'] = df['Agent Name'].fillna(method='ffill')

# This value represents the total amount of time spent in "Unavailable"
df['Code'] = df['Code'].fillna(value='Total')
df.head()


'''
Break Time
Dataframe building and merging
'''
# Create new dataframe for working with Break time
break_df = df[df['Code'] == 'Break']

# Merge in Login Time and Team Name
break_df = pd.merge(break_df, summary[['Login Time', 'Agent Name']])
break_df = pd.merge(break_df, agentlist[['Team Name (ID)', 'Agent Name']])

# Drop Code column
break_df = break_df.drop(columns='Code')

'''
Data wrangling and feature engineering
'''
# Remove all teams other than HERE:
break_df = break_df.where(
    break_df['Team Name (ID)'] == 'Here Navigation (205587)')
break_df = break_df.dropna()

# Change Login Time and Duration from str to time
break_df['Login Time'] = pd.to_timedelta(break_df['Login Time'])
break_df['Duration'] = pd.to_timedelta(break_df['Duration in Seconds'],
                                        unit='Seconds')

# Add new column for percent of time logged in spent in break
break_df['Percent'] = break_df['Duration']/break_df['Login Time']

# Create index for Web (Paper) Agents and drop them from dataframe
paper_agents_index = break_df[break_df['Agent Name'].str.contains
                               ('Paper')].index
break_df.drop(paper_agents_index, inplace=True)

# Clean agent names
break_df['Agent Name'] = break_df['Agent Name'].str.replace(
    '(', '').str.replace(')', '').str.replace('0', '').str.replace(
    '1', '').str.replace('2', '').str.replace('3', '').str.replace(
    '4', '').str.replace('5', '').str.replace('6', '').str.replace(
    '7', '').str.replace('8', '').str.replace('9', '')

# Sort by highest Case Work duration
break_df = break_df.sort_values('Duration', ascending=False)

# Define Break Compliance (108% of total break time)
break_time = (.5/8)
break_compliance_basic = 1.08
raw_break_compliance = break_time + (break_time*.08)
print(f'Break time: {break_time}')
print(f'Raw Break compliance: {raw_break_compliance}')

# Change percent to more understandable number
mult_num = break_compliance_basic/raw_break_compliance
break_df['Percent'] = break_df['Percent']*mult_num
print(f'Break compliance: {break_compliance_basic} (108%)')

# Drop Team Name column
break_df = break_df.drop(columns=['Team Name (ID)', 'Duration in Seconds'])

# Reorder columns
break_df = break_df[['Agent Name', 'Login Time', 'Duration', 'Percent']]

# Change time from days to hours
break_df['Login Time'] = break_df['Login Time']*24
break_df['Duration'] = break_df['Duration']*24


'''
Unavailable Time -- "Case Work", "Technical Difficulties", and "Unavailable"
Dataframe building and merging
'''
# Create new dataframe for adding in 'Case Work', 'Tech Diff', and 'Unavailable'
# Start with Unavailable (since everyone is in Unavailable at some point)
full_un = df[df['Code'] == 'Unavailable']
full_un = full_un.rename(
    columns={'Duration in Seconds': 'Unavailable in Seconds'})

# Create dataframe for Technical Difficulties
tech_diff = df[df['Code'] == 'Technical Difficulties']
tech_diff = tech_diff.rename(
    columns={'Duration in Seconds': 'Tech Diff in Seconds'})

# Create dataframe for Case Work
case_work_2 = df[df['Code'] == 'Case Work']
case_work_2 = case_work_2.rename(
    columns={'Duration in Seconds': 'Case Work in Seconds'})

# Merge in Tech Diff and Unavailable
full_un = pd.merge(full_un,
                   tech_diff[['Tech Diff in Seconds', 'Agent Name']],
                   how='left')
full_un = pd.merge(full_un,
                   case_work_2[['Case Work in Seconds', 'Agent Name']],
                   how='left')

# Merge in Login Time and Agent List
full_un = pd.merge(full_un, summary[['Login Time', 'Agent Name']])
full_un = pd.merge(full_un, agentlist[['Team Name (ID)', 'Agent Name']])

'''
Feature Engineering
'''
# Fill NaN (avoid issue with creating Total Unavailable column)
full_un = full_un.fillna(value=0)

# Change Login Time, Unavailable, Tech Diff, and Case Work from str to time
full_un['Login Time'] = pd.to_timedelta(full_un['Login Time'])
full_un['Unavailable'] = pd.to_timedelta(full_un['Unavailable in Seconds'],
                                        unit='Seconds')
full_un['Tech Diff'] = pd.to_timedelta(full_un['Tech Diff in Seconds'],
                                      unit='Seconds')
full_un['Case Work'] = pd.to_timedelta(full_un['Case Work in Seconds'],
                                      unit='Seconds')

# Change time from days to hours
full_un['Login Time'] = full_un['Login Time']*24
full_un['Unavailable'] = full_un['Unavailable']*24
full_un['Tech Diff'] = full_un['Tech Diff']*24
full_un['Case Work'] = full_un['Case Work']*24

# Create new column for Total Unavailable Time
#  - Specifically: Case Work, Technical Difficulties, and Unavailable
full_un['Total Unavailable'] = full_un['Unavailable'] + full_un['Tech Diff'] + full_un['Case Work']

# Add new columns for percent of time logged in spent in each code
full_un['Unavailable %'] = full_un['Unavailable']/full_un['Login Time']
full_un['Tech Diff %'] = full_un['Tech Diff']/full_un['Login Time']
full_un['Case Work %'] = full_un['Case Work']/full_un['Login Time']
full_un['Total Percent'] = full_un['Total Unavailable']/full_un['Login Time']

'''
Final Cleaning
'''
# Create index for Web (Paper) Agents and drop them from dataframe
paper_agents_index = full_un[full_un['Agent Name'].str.contains
                               ('Paper')].index
full_un.drop(paper_agents_index, inplace=True)

# Clean agent names
full_un['Agent Name'] = full_un['Agent Name'].str.replace(
    '(', '').str.replace(')', '').str.replace('0', '').str.replace(
    '1', '').str.replace('2', '').str.replace('3', '').str.replace(
    '4', '').str.replace('5', '').str.replace('6', '').str.replace(
    '7', '').str.replace('8', '').str.replace('9', '')

# Change percent to whole number
full_un['Unavailable %'] = full_un['Unavailable %']
full_un['Tech Diff %'] = full_un['Tech Diff %']
full_un['Case Work %'] = full_un['Case Work %']
full_un['Total Percent'] = full_un['Total Percent']

full_un = full_un[full_un['Team Name (ID)'] == 'Here Navigation (205587)']

# Drop irrelevant columns
full_un = full_un.drop(columns={'Code', 'Duration', 'Unavailable in Seconds',
                                'Tech Diff in Seconds', 'Case Work in Seconds',
                                'Team Name (ID)'})
