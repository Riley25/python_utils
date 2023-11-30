from datetime import datetime, timedelta, date

# TIME RIGHT NOW
time_now = datetime.now()


UTC_TIME = time_now.strftime('%A %B %d, %Y (%I:%M %p)') 

ET_TIME = time_now - timedelta(hours = 5)
ET_TIME = ET_TIME.strftime('%A %B %d, %Y (%I:%M %p)') 


print('UTC TIME: ' + UTC_TIME)
print(' ET TIME: ' + ET_TIME)





