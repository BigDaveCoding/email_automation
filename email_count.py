import imaplib
import json
import email
import email.header from decode_header

with open('email_details.json', 'r') as file:
    credentials = json.load('file')

username = credentials['username']
password = credentials['password']

