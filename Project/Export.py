import pandas as pd
import datetime as dt
from decimal import Decimal

from Agent_Unavailable_Time import break_df, full_un

'''
Export Break Time for Business Desk
'''
# Last name first
break_df = break_df.sort_values('Agent Name', ascending=True)

# Export
break_df.to_excel(r'C:\Users\awhite_c\Downloads\Break Time (insert date).xlsx')


'''
Export for Business Desk
'''
# Sort by Agent Name
full_un = full_un.sort_values('Agent Name', ascending=True)

# Export
full_un.to_excel(r'C:\Users\awhite_c\Downloads\Unavailable Time (insert date).xlsx')
