import imaplib
import json
import email
from email.header import decode_header

# Load credentials from JSON file

with open('email_details.json', 'r') as file:
    credentials = json.load('file')

username = credentials['username']
password = credentials['password']

# Connect to 123-reg's IMAP server

def conncetEmail():
    mail = imaplib.IMAP4_SSL("imap.123-reg.co.uk")
    mail.login(username, password)
    mail.select("inbox")

    print("Connected to email server")
    return mail

