import pandas as pd
import datetime as dt
from decimal import Decimal
import os

from Agent_Unavailable_Time import break_df, full_un

# Set username from .env
username = os.getenv('username')

'''
Export Break Time for Business Desk
'''
# Last name first
break_df = break_df.sort_values('Agent Name', ascending=True)

# Export
break_df.to_excel(fr'/Users/{username}/Downloads/Break Time (insert date).xlsx')


'''
Export for Business Desk
'''
# Sort by Agent Name
full_un = full_un.sort_values('Agent Name', ascending=True)

# Export
full_un.to_excel(fr'/Users/{username}/Downloads/Unavailable Time (insert date).xlsx')

print('Export complete')
