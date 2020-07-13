import pandas as pd

# Set username from .env
username = os.getenv('username')

'''
Emails
'''
# Read in dataframe
emails = pd.read_excel(fr'/Users/{username}/Downloads/SF Email Report.xlsx')

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
