import pandas as pd
import numpy as np
from decouple import config

# Set username from .env
username = config('username')

'''
Emails
'''
# Read in dataframe
emails = pd.read_csv(fr'/Users/{username}/Downloads/SF Email Report.csv')

# Filter out phone cases (etc.)
emails = emails[emails['Case Origin'] == 'Email']

# Define function to filter on strings
def Drop_cases(df, column, string):
    new_index = df[column.str.contains(string)].index
    df.drop(new_index, inplace=True)

# Filter out EMEA and SUP cases
Drop_cases(emails, emails['Queue Name'], 'EMEA')
Drop_cases(emails, emails['Queue Name'], 'SUPERVISOR')

# Find average age of emails
avg_email = np.mean(emails['Age (Hours)'])
print('')
print(f'Average email age (hours): {avg_email}')

# Look at number of emails in queue
print(f'Number of emails in queue: {len(emails)}')
print('')
