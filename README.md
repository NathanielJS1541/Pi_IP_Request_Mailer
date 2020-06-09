# Pi_IP_Request_Mailer
This is a Python script written for the Raspberry Pi which monitors a Gmail inbox and
responds to any emails with a pre-defined subject with the local IP addresses of all network
interfaces. This program should be set up to run at regular intervals, as it needs to regularly
check the inbox for new requests.

## Requirements
* **`cron`** - For this to work as intended, you will need to schedule tasks with `cron`
(detailed instructions below)
* **A Gmail account** - just because you _can_ use an existing Gmail account for
this doesn't mean that you _should_. It is recommended that you create a **NEW** Gmail
account specifically for this purpose since the password for the account will be stored in
**plaintext** and I am unable to find a way around this. You will also need to enable
the Gmail API (Details to follow), which reduces the security of your account.
* **Python 3**

## Setup
### Account Configuration
After (hopefully) creating a new Gmail account (without 2FA unless you know how to modify 
the code), you need to turn **ON** _Less secure app access_ under the _Security_ tab of 
_Manage My Account_. This allows the Python code send and receive Emails using your Gmail
account.

Next, move the script (`Pi_IP_Request_Mailer.py`) somewhere permanent on your Raspberry Pi, and
open it with a text editor such as nano: `nano Pi_IP_Request_Mailer.py`. You need to add your new 
Gmail account and password into the definitions at the top. Put your new Gmail address
at the variable `gmail_user` and the plaintext password at `gmail_password`. The script will send
the emails to whichever email address requested them. You may also adjust the subject text that the
script is looking for by changing the `REQUEST_KEYWORD` variable.

Finally, ensure that the script is executable by typing `sudo chmod +X Pi_IP_Request_Mailer.py` into
the terminal.

### Script Execution
This python script is intended to be run at short, regular intervals whenever the Pi is running.
This is only a guide, and if you know what you are doing feel free to change this.

The easiest way to schedule tasks on a Raspberry Pi is to use `cron`. Simply type `crontab -e` into a 
terminal. I chose to run this script every minute, so to do this add the following line to the bottom
of the file:
```
*/1 * * * * python3 /home/pi/Documents/Pi_IP_Request_Mailer/Pi_IP_Request_Mailer.py
```
Remember to change the path to match that of your script. If you wanted the script to run every 5 minutes
you would change `*/1` to `*/5`. If you wanted the script to run every hour the line would instead look like
this:
```
* */1 * * * python3 /home/pi/Documents/Pi_IP_Request_Mailer/Pi_IP_Request_Mailer.py
```
I aim with these examples to provide quick and easy setup of the script, not a full tutorial in how to use cron.
The man pages are very helpful if you would like to learn more and can be found by typing `man crontab`.

## Other References
If this isn't quite what you were looking for, try looking at some of these instead:
* [MathWorks' Tutorial to send an email when an IP address changes using ssmtp](https://uk.mathworks.com/help/supportpkg/raspberrypi/ug/configure-raspberry-pi-hardware-to-email-ip-address-changes.html "MathWorks")
* [My Pi_IP_Mailer Repository to automatically Email a specified account whenever it detects an IP address change](https://github.com/NathanielJS1541/Pi_IP_Mailer "Pi_IP_Mailer")
