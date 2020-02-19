import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from decimal import Decimal

'''
Import inContact spreadsheets
'''
# Read in Agent Unavailable Time
df_col_names = ['Agent Name', 'Code', 'Code Type', 'Duration',
                'Duration in Seconds', 'Percent']
df = pd.read_excel(r'C:\Users\awhite_c\Downloads\IC_Reports_AgentUnavailableTime.xlsx',
                   names=df_col_names)

# Read in Agent Summary
summary_col_names = ['Agent Name', 'Handled (Inbound)',
                     'Avg Talk Time (Inbound)', 'Handled (Outbound)',
                     'Avg Talk Time (Outbound)', 'Available Time',
                     'Total Unavailable Time', 'Refused', 'Login Time',
                     'Working Rate', 'Occupancy']
summary = pd.read_excel(r'C:\Users\awhite_c\Downloads\IC_Reports_AgentSummary.xlsx',
                        names=summary_col_names)

# Read in Agent List
agentlist_col_names = ['Team Name (ID)', 'Agent Name', 'Last Login',
                       'Skill Count']
agentlist = pd.read_excel(r'C:\Users\awhite_c\Downloads\IC_Reports_AgentList.xlsx',
                          names=agentlist_col_names)

# Read in Supervisor Snapshot
snapshot_col_names = ['Agent Name', 'Inbound Handled', 'Inbound AHT',
                       'Outbound Handled', 'Outbound AHT', 'Available Time',
                       'Unavailable Time', 'Refused', 'Login Time',
                       'Occupancy']
needed_cols = [0, 2, 6, 8, 9, 13, 14, 21, 23, 29]
snapshot = pd.read_excel(r'C:\Users\awhite_c\Downloads\Supervisor Snapshot.xlsx',
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
nullname_list = boundary_maker(nullname)
needed_rows = len(nullname_list)
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

'''
Visualize Break Time
'''
# Create dataframe of agents who are over break compliance
over_comp = break_df.where(break_df['Percent'] > 1.08)
over_comp = over_comp.dropna()
over_comp['Percent'] = over_comp['Percent']*100
over_comp = over_comp.sort_values('Percent', ascending=False)
print('\nNumber of agents who are over break compliance:', len(over_comp))
print(over_comp)

# Sort values differently for graph
over_comp = over_comp.sort_values('Percent', ascending=True)

# Choose plot style
plt.style.use('ggplot')

# Set styles for axes
plt.rcParams['axes.edgecolor']='#333F4B'
plt.rcParams['axes.linewidth']=0.8
plt.rcParams['xtick.color']='#333F4B'
plt.rcParams['ytick.color']='#333F4B'

# Create for each a horizontal line that starts at x = 0 with the length
# represented by the specific Break percentage value
fig, ax = plt.subplots(figsize=(20, 15))
plt.hlines(y=over_comp['Agent Name'], xmin=0, xmax=over_comp['Percent'],
           color='#268AFF', alpha=0.2, linewidth=5)

# Create dot at the end of the line
plt.plot(over_comp['Percent'], over_comp['Agent Name'], "o", markersize=5,
         color='#268AFF', alpha=0.7)

# Set label style
ax.set_xlabel('Percent', fontsize=15, fontweight='black', color = '#333F4B')
ax.set_ylabel('Agent Name', fontsize=15, fontweight='black', color = '#333F4B')
plt.title(f'Agents Over Break Compliance (108%)',
          fontsize=25, fontweight='black', color = '#333F4B')

# Change the style of the axis spines
ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_smart_bounds(True)
ax.spines['bottom'].set_smart_bounds(True)
plt.show()


'''
Case Work
Dataframe building and merging
'''
# Create new dataframe for working with Case Work time
case_work = df[df['Code'] == 'Case Work']

# Merge in Login Time and Team Name
case_work = pd.merge(case_work, summary[['Login Time', 'Agent Name']])
case_work = pd.merge(case_work, agentlist[['Team Name (ID)', 'Agent Name']])

# Drop Code column
case_work = case_work.drop(columns='Code')

'''
Data wrangling and feature engineering
'''
# Remove all teams other than HERE:
case_work = case_work.where(
    case_work['Team Name (ID)'] == 'Here Navigation (205587)')
case_work = case_work.dropna()

# Change Login Time and Duration from str to time
case_work['Login Time'] = pd.to_timedelta(case_work['Login Time'])
case_work['Duration'] = pd.to_timedelta(case_work['Duration in Seconds'],
                                        unit='Seconds')

# Add new column for percent of time logged in spent in case work
case_work['Percent'] = case_work['Duration']/case_work['Login Time']

# Create index for Web (Paper) Agents and drop them from dataframe
paper_agents_index = case_work[case_work['Agent Name'].str.contains
                               ('Paper')].index
case_work.drop(paper_agents_index, inplace=True)

# Clean agent names
case_work['Agent Name'] = case_work['Agent Name'].str.replace(
    '(', '').str.replace(')', '').str.replace('0', '').str.replace(
    '1', '').str.replace('2', '').str.replace('3', '').str.replace(
    '4', '').str.replace('5', '').str.replace('6', '').str.replace(
    '7', '').str.replace('8', '').str.replace('9', '')

# Change percent to whole number
case_work['Percent'] = case_work['Percent'] * 100

# Limit Percent to 4 decimal places
case_work['Percent'] = round(case_work['Percent'].astype(float),1)

# Rename Login Time
case_work = case_work.rename(
    columns={'Login Time': 'Total Time Logged In'})

# Drop Team Name column
case_work = case_work.drop(columns='Team Name (ID)')

'''
Visualize Case Work
'''
# Create dataframe of agents who spent over 10% of their time in Case Work
high_cw = case_work.where(case_work['Percent'] >= 10)
high_cw = high_cw.dropna()
high_cw = high_cw.sort_values('Percent', ascending=False)
print('\nNumber of agents who spend more than 10% of their time in Case Work:',
      len(high_cw))
print(high_cw)

# Sort values differently for graph
high_cw = high_cw.sort_values('Percent', ascending=True)

# Choose plot style
plt.style.use('ggplot')

# Set styles for axes
plt.rcParams['axes.edgecolor']='#333F4B'
plt.rcParams['axes.linewidth']=0.8
plt.rcParams['xtick.color']='#333F4B'
plt.rcParams['ytick.color']='#333F4B'

# Create for each a horizontal line that starts at x = 0 with the length
# represented by the specific Case Work percentage value
fig, ax = plt.subplots(figsize=(20, 10))
plt.hlines(y=high_cw['Agent Name'], xmin=0, xmax=high_cw['Percent'],
           color='#EF6B22', alpha=0.2, linewidth=5)

# Create dot at the end of the line
plt.plot(high_cw['Percent'], high_cw['Agent Name'], "o", markersize=5,
         color='#EF6B22', alpha=0.7)

# Set label style
ax.set_xlabel('Percent', fontsize=15, fontweight='black', color = '#333F4B')
ax.set_ylabel('Agent Name', fontsize=15, fontweight='black', color = '#333F4B')
plt.title('Agents with Case Work\nabove 10% of Total Time',
          fontsize=25, fontweight='black', color = '#333F4B')

# Change the style of the axis spines
ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_smart_bounds(True)
ax.spines['bottom'].set_smart_bounds(True)
plt.show()


'''
Average Handle Time
'''
# Change values in time columns from str to timedelta
snapshot['Inbound AHT'] = pd.to_timedelta(snapshot['Inbound AHT'])
snapshot['Outbound AHT'] = pd.to_timedelta(snapshot['Outbound AHT'])
snapshot['Available Time'] = pd.to_timedelta(snapshot['Available Time'])
snapshot['Unavailable Time'] = pd.to_timedelta(snapshot['Unavailable Time'])
snapshot['Login Time'] = pd.to_timedelta(snapshot['Login Time'])

# Create new dataframe of agents with concerning Average Handle Time
high_AHT = snapshot[snapshot['Inbound AHT'] > pd.Timedelta('13 min')]
low_AHT = snapshot[snapshot['Inbound AHT'] < pd.Timedelta('5 min')]

# Put the two together and remove zeros
concerning_AHT = pd.concat([high_AHT, low_AHT])
concerning_AHT = concerning_AHT[
    concerning_AHT['Inbound AHT'] != pd.Timedelta('0 min')]

#
concerning_AHT = concerning_AHT.sort_values('Inbound AHT', ascending=True)
print('\nAgents with potentially concerning average handle times:',
    len(concerning_AHT))
print(concerning_AHT)


'''
Average Working Rate
'''
# Convert Working Rate to float and calcualate mean (the goal is at least 80%)
summary['Working Rate'] = summary['Working Rate'].str.strip('%').astype(float)
raw_mean = Decimal(summary['Working Rate'].mean())
avg_work_rt = round(raw_mean,2)
print(f'\nAverage Working Rate: {avg_work_rt}%')
