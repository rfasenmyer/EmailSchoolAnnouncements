#WatchWebAnnouncements.py
#Ryan Fasenmyer 8/31/2019

#Log file name
logFileName = "AnnouncementCheckLog.txt"

#Sending email address
me = "******@gmail.com"

#Recipient emial addresses
recipients = '*****@gmail.com, ********@gmail.com'

# url to be scraped
url = "https://announcementwebpage.com"



#Watch the program to make sure it completes succesfullly
watchdogURL = "http://watchdogURL.com"

import hashlib
import urllib2
import random
import time
import smtplib
import datetime
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import logging #used for debugging issues.
logging.basicConfig(
    filename=logFileName,
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

import os.path
from os import path

def getHash(html):
    return hashlib.sha224(html).hexdigest()


def getWebPage():
    # random integer to select user agent
    randomint = random.randint(0,7)

    # User_Agents
    # This helps skirt a bit around servers that detect repeaded requests from the same machine.
    # This will not prevent your IP from getting banned but will help a bit by pretending to be different browsers
    # and operating systems.
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:8.0.1) Gecko/20100101 Firefox/8.0.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19'
    ]

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', user_agents[randomint])]
    response = opener.open(url)
    the_page = response.read()

    return the_page



def getAnnouncement(html):
    start = '<h1>Announcements</h1>'
    end = '<h2>Archive</h2>'
    startPosition = html.find(start)
    endPosition = html.find(end)

    announcement = html[startPosition:endPosition]
    return announcement

def sendEmail(strTo,strFrom,strSubject,strBody):

    # Create message container - the correct MIME type is multipart/alternative.
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = strSubject
    msg['From'] = strFrom
    msg['To'] = strTo

    # Create the body of the message (a plain-text and an HTML version).
    text = "The latest announcements"
    html = strBody

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)


    gmail_user = '*******@gmail.com'
    gmail_password = '******'

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
    except:
        print 'Something went wrong...'

    # Send the message via local SMTP server.
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(strFrom, msg["To"].split(","), msg.as_string())
    server.quit()




#get current webpage
print('Get current web page')
currentPage = getWebPage() 

print('Get current hash')
currentHash = getHash(getAnnouncement(currentPage))

#Load previous hash
#print(path.exists('announcement.hash'))
if path.exists('announcement.hash'):
    #Load hash file
    print('Previous hash file found, opening and obtaining hash')
    with open('announcement.hash', 'r') as hashfile:
        varPreviousHash = hashfile.read()
        print('Previous hash ' + str(varPreviousHash))
    #Check previous hash with new hash.  If they do not match, update the hash and send an email notificataion.
    if str(varPreviousHash) == str(currentHash):
        print('No hash change')
    else:
        print('Hash has changed.  Send email notification.')
        print('Old hash = ' + str(varPreviousHash))
        print('New hash = ' + str(currentHash))  
      #Parse out announcement
        announcementHtml = getAnnouncement(currentPage)
        sendEmail(recipients,me,"Web Page Announcements",announcementHtml)
        print('Email notification sent.')

        #Write hash to text file.
        print('Writing new hash to file')



        file = open('announcement.hash', 'w+')
        file.write(str(currentHash))
        file.close()
        print('Hash file written')
else:
    #Create hash file
    print("No file present.  Creating file")
    file = open('announcement.hash', 'w+')
    file.write(str(currentHash))
    file.close()

    #Send email notification
    #Parse out announcement
    announcementHtml = getAnnouncement(currentPage)
    sendEmail(recipients,me,"Web Page Announcements",announcementHtml)
    print('Email notification sent')

#Sendwatchdog healthchecks.io notification so that I know the script completed successfully
requests.request("GET", watchdogURL)
print('Watchdog checkin complete')

#Get current date and time
ts = time.time() #Get epoc time
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
#Send message to the command line
print(st + " Program completed successfully!")


