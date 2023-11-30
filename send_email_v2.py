def send_email( email_receiver , file_path , buy = True):
        
    import smtplib
    import ssl
    from email.message import EmailMessage
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders

    # Define email sender and receiver
    email_sender = 'option.notify@gmail.com'
    email_password = 'jvbsjwmkghfxusls'

    # Set the subject and body of the email    
    subject = 'Option Update'
    if buy == True:
        body = """
        <h2 style="font-family: Calibri Light";>SPY Report</h2>
        <p style="font-family: Calibri Light ; font-size: 20px">The market is being <strong>oversold</strong>. Time to buy a <strong>call</strong>.</p>
        <br></br>
        <p style="font-family: Calibri Light ; font-size: 20px"> STOCK V.I.S. </p>
        <p style="font-family: Calibri Light ; font-size: 20px" >(Stock Value Intelligence System)</p>
        """
    elif buy == False:
        body = """
        <h2 style="font-family: Calibri Light";>SPY Report</h2>
        <p style="font-family: Calibri Light ; font-size: 20px">The market is being <strong>overbought</strong>. Time to buy a <strong>put</strong>.</p>
        <br></br>
        <p style="font-family: Calibri Light ; font-size: 20px"> STOCK V.I.S. </p>
        <p style="font-family: Calibri Light ; font-size: 20px" >(Stock Value Intelligence System)</p>
        """

    email = MIMEMultipart()
    email["From"] = email_sender
    email["To"] = email_receiver
    email["Subject"] = "Option Update"


    msgText = MIMEText(body, 'html')
    email.attach(msgText)


    
    # open the file in bynary
    binary_pdf = open(file_path, 'rb')
    
    payload = MIMEBase('application', 'octate-stream', Name=file_path)
    payload.set_payload((binary_pdf).read())
    
    # enconding the binary into base64
    encoders.encode_base64(payload)
    
    # add header with pdf name
    payload.add_header('Content-Decomposition', 'attachment', filename=file_path)
    email.attach(payload)
    
    # best way to attach a PDF
    #with open(file_path, 'rb') as fp:
    #    img = MIMEImage(fp.read())
    #    img.add_header('Content', 'attachment', filename=file_path)
    #    email.attach(img)
    # Add SSL (layer of security)

    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, email.as_string())

#send_email( 'riley.heiman2@gmail.com' , 'email_plots/' + '2-17-2023' + '.png' , buy = True)


