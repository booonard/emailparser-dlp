import argparse
import random
from random import randint
from random import randrange
from string import Template
import uuid
import datetime
import hashlib

def valid_number(value):
    n = int(value)
    if n < 1 or n > 100:
        raise argparse.ArgumentTypeError("{} is not a valid number".format(n))
    return n

def generate_alert(since):
    
    # generate sensitive data
    matches = []
    matches_string = ""
    for i in range(randrange(1,10)):
        cc = random.choice(credit_card_numbers).strip()
        matches.append(cc)
        matches_string += cc + "\n"
    match_count = len(matches)

    # generate the attchment to the alert 
    sentence = random.choice(sentences).strip()
    words = list(sentence.split())
    for cc in matches:
        i = random.randint(0, len(words))
        words.insert(i, cc)
    attachment_content = " ".join(words)

    # generate data for alert
    transaction_id = uuid.uuid4()
    url = random.choice(urls).strip()
    site_category = random.choice(site_types).strip()
    user = random.choice(first_names).strip().lower() + "." + random.choice(surnames).strip().lower() + "@somecompany.com.au"
    ip_address = "10.0.{}.{}".format(randint(0,255), randint(0,255))

    timestamp = since + datetime.timedelta(minutes=randrange(10))
    timestamp_readable = timestamp.strftime('%a %b %d %H:%M:%S %Y')

    email_subject = "Web DLP Violation - {} [{}]".format(user,transaction_id)

    attachment_filename = random.choice(filenames).strip()
    attachment_metadata = str(attachment_content)
    file_md5 = hashlib.md5(attachment_metadata.encode()).hexdigest()

    # populate the alert template 
    email_template = Template(email_alert)
    alert_email = email_template.safe_substitute( 
        TO_ADDRESS = to_address, \
        SUBJECT = email_subject, \
        TRANSACTION_ID = transaction_id, \
        USER = user, \
        IP = ip_address, \
        URL = url, \
        TYPE = site_category, \
        TIMESTAMP = timestamp_readable, \
        DLPMD5 = file_md5, \
        MATCH_COUNT = match_count, \
        ATTACHMENT_FILENAME = attachment_filename,
        MATCHED_LIST = matches_string, \
        ATTACHMENT_CONTENT = attachment_content)

    alert_details = {
        "timestamp": timestamp, \
        "alert_email": alert_email
    }
    return(alert_details)

def output_local_filesystem(alert_email):
    print("creating file on local filesystem")

def output_ses(alert_email):
    print("sending email via ses")

def output_s3(alert_email):
    print("uploading file to s3")


parser = argparse.ArgumentParser()
parser.add_argument("-n", default=10, type=valid_number)
parser.add_argument("-o", default="local", type=str, choices=["local", "ses", "s3"])

args = parser.parse_args()
num_alerts = args.n
output_type = args.o

to_address = "mailparsertest@devnard.net"

# load email template
email_alert_file = open("test-notification-email.txt")
email_alert = email_alert_file.read()
email_alert_file.close() 

# load test data
credit_card_numbers_file = open("data/credit-card-numbers.txt")
credit_card_numbers = credit_card_numbers_file.readlines()
credit_card_numbers_file.close() 

urls_file = open("data/urls.txt")
urls = urls_file.readlines()
urls_file.close() 

site_types_file = open("data/zs-categories.txt")
site_types = site_types_file.readlines()
site_types_file.close() 

first_names_file = open("data/first-names.txt", "r")
first_names = first_names_file.readlines()
first_names_file.close()

surnames_file = open("data/surnames.txt", "r")
surnames = surnames_file.readlines()
surnames_file.close()

filenames_file = open("data/filenames.txt", "r")
filenames = filenames_file.readlines()
filenames_file.close()

sentences_file = open("data/sentences.txt", "r")
sentences = sentences_file.readlines()
sentences_file.close()

# start create test email
start_time = datetime.datetime.now()

for n in range(num_alerts):
    alert_details = generate_alert(start_time)
    alert_email = alert_details["alert_email"]
    print(alert_email)

    if output_type == "local":
        output_local_filesystem(alert_email)
    elif output_type == "ses":
        output_ses(alert_email)
    elif output_type == "s3":
        output_s3(alert_email)
    
    alert_time = alert_details["timestamp"]    
    start_time = alert_time
