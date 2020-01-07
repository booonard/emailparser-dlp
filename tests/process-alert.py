
import email
import boto3


ALERT_TOKEN = "The attached content triggered a Web DLP rule for your organisation."
TRANSACTION_ID_TOKEN = "Transaction ID: "
FILENAME_TOKEN = 'filename="'
ALERT_OBJECT_NAME = "alert.txt"


def upload_to_s3(object_data, object_key):
    
    bucket_name = "mailparser-parsedmail"

    client = boto3.client('s3')
    client.put_object(Body=object_data, Bucket=bucket_name, Key=object_key)
    
    print("Uploaded to S3 bucket {} with object name: {}".format(bucket_name, object_key))


print("Processing alert")

email_file = open("s3-input/email-object.txt", "r")
#e = email_file.readlines()
#email_file.close() 

message = email.message_from_file(email_file)
transaction_id = ""

for message_part in message.get_payload():
    #for m in message_part.values()
    
    s = message_part.__str__()
    #print(s)

    i = s.find(ALERT_TOKEN)
    if i > 0: 
        alert_body = s[i:]

        tid_start = alert_body.find(TRANSACTION_ID_TOKEN) + len(TRANSACTION_ID_TOKEN)
        tid_end = alert_body.find("\n", tid_start)
        transaction_id = alert_body[tid_start:tid_end]

        alert_object_key = transaction_id + "/" + ALERT_OBJECT_NAME
        upload_to_s3(alert_body, alert_object_key)

        #print(alert_body)
        #print(transaction_id)

    if "Content-Disposition" in message_part.keys():
        #disposition_value = message_part["Content-Disposition"]
        
        
        filename_start = s.find(FILENAME_TOKEN) + len(FILENAME_TOKEN)
        filename_end = s.find('"', filename_start)
        
        file_content_start = filename_end + 1

        filename = s[filename_start:filename_end]
        file_contents = s[file_content_start:]

        evidence_object_key = transaction_id + "/" + filename
        upload_to_s3(file_contents, evidence_object_key)

        #print("filename: " + filename)
        #print("file contents: " + file_contents)
