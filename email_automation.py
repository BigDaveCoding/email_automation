import imaplib
import email
from email.header import decode_header
import json

# Load credentials from JSON file
with open('email_details.json', 'r') as file:
    credentials = json.load(file)

username = credentials['username']
password = credentials['password']

# Get user inputs for folder name and email address
folder_name = input("Enter the folder name to move emails to: ")
email_address = input("Enter the email address to process: ")

# Connect to 123-reg's IMAP server
mail = imaplib.IMAP4_SSL("imap.123-reg.co.uk")

# Login to your email account
mail.login(username, password)

# Select the inbox
mail.select("inbox")

# Search for all emails from the specific email address
status, messages = mail.search(None, 'FROM', f'"{email_address}"')

# Check if the search was successful
if status != "OK":
    print("No messages found!")
    mail.logout()
    exit()

# Convert the result into a list of email IDs
email_ids = messages[0].split()

# Print the total number of emails found
print(f"Found {len(email_ids)} emails from {email_address}.")

# Create the folder if it doesn't already exist
try:
    mail.create(f'"{folder_name}"')
    print(f"Folder '{folder_name}' created successfully.")
except imaplib.IMAP4.error as e:
    print(f"Folder '{folder_name}' already exists or could not be created: {e}")


# Process the emails in batches to avoid overloading the server
batch_size = 50  # Customize this based on performance
for i in range(0, len(email_ids), batch_size):
    batch = email_ids[i:i+batch_size]
    
    for email_id in batch:
        # Fetch the email by ID
        res, msg = mail.fetch(email_id, "(RFC822)")
        
        if res != "OK":
            print(f"Failed to fetch email ID {email_id}")
            continue
        
        for response_part in msg:
            if isinstance(response_part, tuple):
                # Parse the email into a message object
                msg = email.message_from_bytes(response_part[1])
                
                # Decode the subject of the email
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # Decode from bytes to a string
                    subject = subject.decode(encoding if encoding else "utf-8")
                print(f"Processing email with subject: {subject}")
                
                # Move the email to the specified folder using COPY instead of STORE
                try:
                    copy_status = mail.copy(email_id, f'"{folder_name}"')
                    if copy_status[0] == 'OK':
                        # Mark the email as deleted from the inbox
                        mail.store(email_id, '+FLAGS', '\\Deleted')
                        print(f"Email {email_id} moved to '{folder_name}' and marked as deleted.")
                    else:
                        print(f"Failed to copy email {email_id} to '{folder_name}': {copy_status}")
                except Exception as e:
                    print(f"Failed to move email {email_id} to '{folder_name}': {e}")
                
    # Optionally, print progress after each batch
    print(f"Processed batch {i//batch_size + 1} out of {len(email_ids)//batch_size + 1}")

# Expunge deleted emails
mail.expunge()

# Logout from the server
mail.logout()