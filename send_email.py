#
# PRO: Send_email.py
#
# AUTHOR: R.N.H. 
#
# DATE: 7/7/19
#
# PURPOSE: Send an email message with the intent of automating the process. 
#


import smtplib 

smtpObj = smtplib.SMTP('smtp-mail.outlook.com', 587 )

#         Email providers with SMPT servers
#
#      PROVIDER      SMPT server domain name
#
#      Gmail         smtp.gmail.com
#      Outlook       smtp-mail.outlook.com (port 587)
#      Yahoo         smtp.mail.yahoo.com
#      AT&T          smpt.mail.att.net (port 465)
#      Comcast       smtp.comcast.net
#      Verizon       smtp.verizon.net  (port 465)

smtpObj.ehlo()

smtpObj.starttls()

smtpObj.login('OPTION.NOTIFY@outlook.com','')

msg  = "Subject: So long....\nHello Alice, \n \n I'm glad you found the muffin man on drury lane. \n \n Sincerely, \n \n Bob"

smtpObj.sendmail(
    'OPTION.NOTIFY@outlook.com',  # FROM
    'riley.heiman2@gmail.com',         # TO
    msg )

smtpObj.quit()




