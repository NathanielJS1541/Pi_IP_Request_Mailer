import subprocess
import smtplib
import imaplib
from email import message_from_bytes
from email.mime.text import MIMEText
from datetime import datetime
import socket

"""
For this program to work some setup on your Raspberry Pi is required. First ensure that the program is executable:
sudo chmod +X Pi_IP_Request_Mailer.py

Then use cron to schedule this to run regularly (this example will run the task every two minutes):
Type into the terminal "cron -e".
Then add this line at the bottom of your cron file, remembering to edit the path correctly:
*/2 * * * * python /home/pi/Documents/Pi_IP_Mailer.py

The program will now work as intended. It is also worth noting that storing passwords in plaintext is BAD. PLEASE
create a new email address for this program that is not linked to any of your other accounts and has a unique
password. You will also need to go to your Gmail "Manage your account" settings and under "security" turn access for
"Less secure apps" ON. PLEASE create a separate email for this reason.
"""

REQUEST_KEYWORD = 'IP Request'               # The string to look for in the emails signifying a request

# Account details
gmail_user = 'YOUR_PI_EMAIL@gmail.com'       # Gmail account that the email will be sent from
gmail_password = 'YOUR_PASSWORD'             # Gmail password.
search_folder = 'inbox'

# IMAP server details
imap_server_name = 'imap.gmail.com'
imap_port = 993

# SMTP server details
smtp_server_name = 'smtp.gmail.com'
smtp_port = 587


# Function to read any unread emails in the inbox
def email_request_check():
    imap_server = imaplib.IMAP4_SSL(imap_server_name, imap_port)  # This is the imap server to use
    imap_server.login(gmail_user, gmail_password)                 # Login to the imap server

    imap_server.select(search_folder)                             # Select "inbox" to search through
    # Record email.search()[0] to status and everything else to results
    status, results = imap_server.search(None, '(UNSEEN SUBJECT "%s")' % REQUEST_KEYWORD)

    if status == 'OK':
        # Only continue if there were no errors
        mail_id_list = results[0].decode('utf-8').split()  # Split the email id's into a list after decoding

        # If there are no unread emails, just return
        if len(mail_id_list) == 0:
            print("No unread emails")
            return

        # For every unread email index we were returned do the following
        for i in range(len(mail_id_list)):
            # Fetch the email and return a status too, same as before
            status, fetch = imap_server.fetch(mail_id_list[i], '(RFC822)')
            if status == 'OK':
                # If the email was returned successfully, search through the response and find the sender
                for response_part in fetch:
                    if isinstance(response_part, tuple):
                        sender = message_from_bytes(response_part[1])['From']
                        # Send an email back to the request sender, containing the current Pi IP
                        email_notification(sender, generate_email_body())
                        # Move the read email to the trash
                        imap_server.store(mail_id_list[i], '+X-GM-LABELS', '\\Trash')
            else:
                print("Fetch status code returned: %s" % status)
                return
    else:
        print("Search status code returned: %s" % status)
        return

    imap_server.select('[Gmail]/Trash')              # Move to the trash folder
    imap_server.store("1:*", '+FLAGS', '\\Deleted')  # Mark all items to be deleted
    imap_server.expunge()                            # Delete marked items
    imap_server.close()                              # Close mailboxes
    imap_server.logout()                             # Log out


# Function to send an email to the specified account
def email_notification(request_sender, email_body):
    smtp_server = smtplib.SMTP(smtp_server_name, smtp_port)  # This is the smtp server to use

    smtp_server.ehlo()                                       # Identify device to ESMTP server
    smtp_server.starttls()                                   # Start TLS encryption
    smtp_server.ehlo()
    smtp_server.login(gmail_user, gmail_password)            # Log in to server

    # Compose the message
    email = MIMEText(email_body)
    email['Subject'] = '%s on %s' % (socket.gethostname(), datetime.now().strftime('%d/%m/%Y at %H:%M'))
    email['From'] = gmail_user
    email['To'] = request_sender

    # Send the message
    smtp_server.sendmail(gmail_user, [request_sender], email.as_string())

    # Close connection to server
    smtp_server.quit()


def generate_email_body():
    arg = 'ip route list'                                          # Linux command to list interfaces and IP's
    p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)  # Runs 'arg' in a 'hidden terminal'.
    data = p.communicate()                                         # Get data from 'p terminal'.

    message_body = ""                # Start with a blank message body
    ip_lines = data[0].splitlines()  # Take the input data and split it by line
    """
    data will look something like this:
    -----------------------------------------------------------------------------------
    default via XXX.XXX.XXX.XXX dev usb0 src XXX.XXX.XXX.XXX metric XXX 
    default via XXX.XXX.XXX.XXX dev wlan0 src XXX.XXX.XXX.XXX metric XXX 
    XXX.XXX.XXX.XXX/XX dev wlan0 proto kernel scope link src XXX.XXX.XXX.XXX metric XXX 
    XXX.XXX.XXX.XXX/XX dev usb0 proto kernel scope link src XXX.XXX.XXX.XXX metric XXX 
    -----------------------------------------------------------------------------------
    
    The first two lines are giving details about the default routes for any packet. We
    want to ignore these lines.
    Every interface will have a line after the list of defaults. Therefore, we can look
    for the word "default" in each line, and if we don't find it we can process the line.
    """
    for i in range(0, len(ip_lines)):
        if b'default' not in ip_lines[i]:
            split_line = ip_lines[i].split()  # Split the line into individual words
            """
            The interface name always follows the word "dev", therefore it will be at the index
            after that of the word "dev". It is currently a byte literal, so we convert it into a
            string by decoding it from the UTF-8 format.
            """
            interface_name = split_line[split_line.index(b'dev')+1].decode('utf-8')
            """
            The IP address for that interface always follows the word "src". The same idea
            as before is used, remembering to use the .decode() function.
            """
            assigned_ip = split_line[split_line.index(b'src')+1].decode('utf-8')
            message_body += '%s has been assigned the IP: %s\n' % (interface_name, assigned_ip)  # Compose the email

            return message_body


email_request_check()
