import argparse
import random
from random import randint
from random import randrange
from string import Template
import uuid
import datetime
import hashlib
import boto3

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
    transaction_id = str(uuid.uuid4())
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
        "timestamp": timestamp, 
        "alert_email": alert_email,
        "email_subject" : email_subject, 
        "alert_id": transaction_id
    }
    return(alert_details)


def save_as_file(alert_id, alert_email):

    local_filename = "output/" + alert_id
    alert_file = open(local_filename, "a")
    alert_file.write(alert_email)
    alert_file.close()
    print("Created file " + local_filename)

def email_with_ses(alert_email, email_subject):

    client = boto3.client('ses')

    client.send_raw_email(
        RawMessage={ 'Data': alert_email }
    )

    print("Emailed alert with SES to " + to_address + " with subject " + email_subject)


def upload_to_s3(alert_id, alert_email):
    
    bucket_name = "mailparser-rawmail"

    client = boto3.client('s3')
    client.put_object(Body=alert_email, Bucket=bucket_name, Key=alert_id)
    
    print("Uploaded to S3 bucket {} with object name: {}".format(bucket_name, alert_id))


OUTPUT_TYPE_FILE = "file"
OUTPUT_TYPE_SES = "ses"
OUTPUT_TYPE_S3 = "s3"

parser = argparse.ArgumentParser()
parser.add_argument("-n", default=10, type=valid_number)
parser.add_argument("-o", default=OUTPUT_TYPE_FILE, type=str, choices=[OUTPUT_TYPE_FILE, OUTPUT_TYPE_SES, OUTPUT_TYPE_S3])

args = parser.parse_args()
num_alerts = args.n
output_type = args.o

print("Generating {} alerts for output to {}".format(num_alerts, output_type))
#to_address = "mailparsertest@devnard.net"
to_address = "mailparsertest@devnard.net, booonard@hotmail.com"


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
alert_time_from = datetime.datetime.now()

for n in range(num_alerts):
    alert_details = generate_alert(alert_time_from)
    alert_email = alert_details["alert_email"]
    alert_id = alert_details["alert_id"]
    email_subject = alert_details["email_subject"]

    if output_type == OUTPUT_TYPE_SES:
        email_with_ses(alert_email, email_subject)
    elif output_type == OUTPUT_TYPE_FILE:
        save_as_file(alert_id, alert_email)
    elif output_type == OUTPUT_TYPE_S3:
        upload_to_s3(alert_id, alert_email)       
    
    alert_time_from = alert_details["timestamp"]    
