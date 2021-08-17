To generate "Low utilization Amazon EC2 instances" recommendations, AWS Trusted Advisor currently checks the Amazon Elastic Compute Cloud (Amazon EC2) instances that were running at any time during the last 14 days and alerts if the daily CPU utilization was 10% or less and network I/O was 5 MB or less on 4 or more days. For some customers, due to their use case, a need may arise to look at the other cloudwatch metrics like Disk I/O and Disk R/W bytes for a more detailed analysis.

https://aws.amazon.com/premiumsupport/technology/trusted-advisor/best-practice-checklist

This tool provides an easy and automated to fetch cloudwatch metrics for any EC2 instances. When the source file with a list of EC2 instances is uploaded to S3 (under a predecided prefix), a lambda function split.py gets triggered. This lambda splits the main csv file into a separate file (per instance) and then uploads them to S3 (another prefix). Each file upload operation triggers another lambda fetch.py, of its own, which then fetches the metrics from Amazon Cloudwatch and uploads to S3. The purpose of splitting the file is to enable parallelism and keep the execution time < 15 mins.

This tool currently fetches last 15 days metrics for all supported CloudWatch metrics for EC2 instances and EBS volumes. The list and the date range can be further customized depending on the use case. Please read below link before making any changes 

https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html

**Input and Output:**
You can use a list of EC2 instance ID as an input. You can download the Low Utilization As an output, a separate file per instance with selected cloudwatch metrics is returned and uploaded to S3 bucket. Please refer to sample input and output file. 

**Configuration Steps:**


**Constraints:**
While further enhancements are underway, the current solution is limited to per region per account.

![Workflow](images/workflow.png)
