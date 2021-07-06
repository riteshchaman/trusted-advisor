import json
import boto3
import os
import csv

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
split_location='trustedadvisorfile/split/'

rows_per_csv = 1

def lambda_handler(event, context):
    print (event)
    # Get the object from the event and show its content type
    #bucketname = event['requestPayload']['Records'][0]['s3']['bucket']['name']
    bucketname = event['Records'][0]['s3']['bucket']['name']
    print (bucketname)
    #objectname = event['requestPayload']['Records'][0]['s3']['object']['key']
    objectname = event['Records'][0]['s3']['object']['key']
    print(objectname)
    s3.Bucket(bucketname).download_file(objectname, '/tmp/file.csv')
    

    with open('/tmp/file.csv') as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames
        rows = [row for row in reader]
        pages = []

        row_count = len(rows)
        start_index = 0
        # here, we slice the total rows into pages, each page having [row_per_csv] rows
        while start_index < row_count:
            pages.append(rows[start_index: start_index+rows_per_csv])
            start_index += rows_per_csv

        for i, page in enumerate(pages):
            local_pcsd_file='/tmp/split_{}.csv'.format(i+1)
            s3_pcsd_file='split_{}.csv'.format(i+1)
            with open(local_pcsd_file, 'w+') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=header)
                writer.writeheader()
                for row in page:
                    writer.writerow(row)
            s3_client.upload_file(local_pcsd_file, 'arubatesting', 'split/'+s3_pcsd_file)
            
        linux=os.system('ls -l /tmp')
        print (linux)



