import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_register_email(user, link):
    # me == my email address
    # you == recipient's email address
    me = "cs390mylink@gmail.com"
    you = user

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "MyLink Registration"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    text = "CS390 MyLink\n"
    html = """\
    <html>
      <head></head>
      <body>
        <p>Welcme to CS390 MyLink!<br>
           After clicking the link below, you will become an active member of the community.<br>
           Click <a href="{link}">here</a> to verify your account.
        </p>
      </body>
    </html>
    """.format(link=link)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login('cs390mylink@gmail.com', 'CS390link')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    mail.sendmail(me, you, msg.as_string())
    mail.quit()


