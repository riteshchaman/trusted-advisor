import json,os
import csv
import boto3
import datetime
from botocore.config import Config
from csv import DictReader


def lambda_handler(event, context):
    
    def fetch_metrics(Namespace,MetricName,Name,Value):
        fetch_metrics = client.get_metric_statistics(
            Namespace=Namespace,
            MetricName=MetricName,
            Dimensions=[
                {
                    'Name': Name,
                    'Value': Value
                },
                ],
                StartTime=startdate,
                EndTime=enddate,
                Statistics=['Maximum'],
                Period=86400
                )
        final_list=[]
        for i in range(len(fetch_metrics['Datapoints'])):
            final_list.append(fetch_metrics['Datapoints'][i]['Maximum'])
        return final_list
        
    def dump_csv_header():
        with open(local_file , 'w', newline='') as outfile:
            Header=['Region','Namespace','InstanceId','ResourceName','MetricsName','Tags','Day1','Day2','Day3','Day4','Day5','Day6','Day7','Day8','Day9','Day10','Day11','Day12','Day13','Day14','Day15']
            writer = csv.DictWriter(outfile, fieldnames=Header)
            writer.writeheader()
            
    def dump_csv_rows(final_list,region,namespace,resourcename,metricsname):
        if (len(final_list) == 15):
            print(metricsname,namespace,len(final_list),resourcename)
            with open(local_file , 'a', newline='') as outfile:
                Header=['Region','Namespace','InstanceId','ResourceName','MetricsName','Tags','Day1','Day2','Day3','Day4','Day5','Day6','Day7','Day8','Day9','Day10','Day11','Day12','Day13','Day14','Day15']
                writer = csv.DictWriter(outfile, fieldnames=Header)
                writer.writerow({'Region':region,'Namespace':namespace,'InstanceId':instanceid,'ResourceName':resourcename,'MetricsName':metricsname,'Tags':tags,'Day1':final_list[0],'Day2':final_list[1],'Day3':final_list[2],'Day4':final_list[3],'Day5':final_list[4],'Day6':final_list[5],'Day7':final_list[6],'Day8':final_list[7],'Day9':final_list[8],'Day10':final_list[9],'Day11':final_list[10],'Day12':final_list[11],'Day13':final_list[12],'Day14':final_list[13],'Day15':final_list[14]})
	
    
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3')
    ec2client = boto3.client('ec2')

    startdate = datetime.datetime.today() - datetime.timedelta(days=15)
    enddate = datetime.datetime.today()
    
    
    ec2_metrics_list=['CPUUtilization','DiskReadOps','NetworkIn','NetworkOut','DiskReadBytes','DiskWriteBytes','NetworkPacketsIn','NetworkPacketsOut','EBSReadOps','EBSWriteOps','EBSReadBytes','EBSWriteBytes']
    ebs_metrics_list=['VolumeReadBytes','VolumeWriteBytes','VolumeReadOps','VolumeWriteOps','BurstBalance']
    
    bucketname = event['Records'][0]['s3']['bucket']['name']
    objectname = event['Records'][0]['s3']['object']['key']
    
	#Downloading split file to parse 
    s3.Bucket(bucketname).download_file(objectname, '/tmp/file.csv')
    
    #Parse the csv to extract instanceid, region
    with open('/tmp/file.csv', 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        for row in csv_dict_reader:
            AZ=row['\ufeffRegion/AZ']
            region=AZ[:-1]
            instanceid=row['Instance ID']
            
    client = boto3.client('cloudwatch', region_name=region)
    ec2 = boto3.resource('ec2', region_name=region)
    
    local_file='/tmp/'+instanceid+'.csv'
    
    
    #Fetch EBS volumes attached to Instance#
           
    instance = ec2.Instance(instanceid)
    tags=instance.tags
    ebs=[]
    for device in instance.block_device_mappings:
     	volume = device.get('Ebs')
     	ebs.append(volume.get('VolumeId'))
     		
    #Dump CSV header and rows   
    dump_csv_header()
        
    for MetricName in ec2_metrics_list:
    	ec2_metrics=fetch_metrics('AWS/EC2',MetricName,'InstanceId',instanceid)
    	dump_csv_rows(ec2_metrics,region,'AWS/EC2',instanceid,MetricName)
    	
    for volumeid in ebs:
    	for MetricName in ebs_metrics_list:
    		ebs_metrics=fetch_metrics('AWS/EBS',MetricName,'VolumeId',volumeid)
    		dump_csv_rows(ebs_metrics,region,'AWS/EBS',volumeid,MetricName)
    

	#Upload Final CSV file to S3 
    s3_client.upload_file(local_file, 'arubatesting', 'processed/'+instanceid+'-'+enddate.strftime('%Y-%m-%d')+'.csv')	
		
