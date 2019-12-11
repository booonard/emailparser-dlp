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
    
    # create payload for attachment

    # load data - from dictionary
    # <URL> <TYPE> <ENGINES> <DICTIONARIES> <TRIGGERS>
    url = random.choice(urls).strip()
    site_category = random.choice(site_types).strip()
    dlp_engine = random.choice(dlp_engines).strip()
    dlp_dictionary = random.choice(dlp_dictionaries).strip()

    # load data - generated
    # <TRANSACTION_ID> <USER> <IP> <TIMESTAMP> <DLPMD5>
    transaction_id = uuid.uuid4()
    user = random.choice(first_names).strip().lower() + "." + random.choice(surnames).strip().lower() + "@somecompany.com.au"
    ip_address = "10.0.{}.{}".format(randint(0,255), randint(0,255))

    timestamp = since + datetime.timedelta(minutes=randrange(10))
    timestamp_readable = timestamp.strftime('%a %b %d %H:%M:%S %Y')

    file_metadata = str(transaction_id)
    file_md5 = hashlib.md5(file_metadata.encode()).hexdigest()

    alert_details = {
        "timestamp": timestamp
    }

    email_template = Template(email_alert)
    email = email_template.safe_substitute( \
        TRANSACTION_ID = transaction_id, \
        USER = user, \
        IP = ip_address, \
        URL = url, \
        TYPE = site_category, \
        TIMESTAMP = timestamp_readable, \
        DLPMD5 = file_md5, \
        ENGINES = dlp_engine, \
        DICTIONARIES = dlp_dictionary)
    print(email)
    return(alert_details)

parser = argparse.ArgumentParser()
parser.add_argument("-n", default=10, type=valid_number)
parser.add_argument("-o", default="local", type=str, choices=["local", "ses", "s3"])

args = parser.parse_args()
num_alerts = args.n
output_type = args.o

# load email template
email_alert_file = open("test-notification-email.txt")
email_alert = email_alert_file.read()
email_alert_file.close() 

# load test data
urls_file = open("data/urls.txt")
urls = urls_file.readlines()
urls_file.close() 

site_types_file = open("data/zs-categories.txt")
site_types = site_types_file.readlines()
site_types_file.close() 

dlp_engines_file = open("data/zs-dlp-engines.txt")
dlp_engines = dlp_engines_file.readlines()
dlp_engines_file.close()

dlp_dictionaries_file = open('data/zs-dlp-dictionaries.txt')
dlp_dictionaries = dlp_dictionaries_file.readlines()
dlp_dictionaries_file.close()

first_names_file = open("data/first-names.txt", "r")
first_names = first_names_file.readlines()
first_names_file.close()

surnames_file = open("data/surnames.txt", "r")
surnames = surnames_file.readlines()
surnames_file.close()

# start create test email
start_time = datetime.datetime.now()

for n in range(num_alerts):
    alert_details = generate_alert(start_time)
    alert_time = alert_details["timestamp"]    
    start_time = alert_time
