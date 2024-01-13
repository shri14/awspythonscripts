import boto3
import pandas as pd
import os

# Initialize AWS S3 client
s3 = boto3.client('s3')

# Specify the S3 bucket and prefix where the reports are stored
s3_bucket = 'bil2323'
s3_prefix = 'reports/'  # Specify the prefix you used during report configuration

# List IAM users (replace with actual IAM usernames or identifiers)
iam_users = ['Abhijit_Shinde', 'Ajay_Patil', 'Anshu_Das']

# Process and analyze reports for each IAM user
for user in iam_users:
    # Construct the S3 report path
    report_path = f's3://{s3_bucket}/{s3_prefix}/{user}-your-report-name.csv'

    # Download the report
    report_file_name = f'{user}-report.csv'
    s3.download_file(s3_bucket, f'{s3_prefix}/{user}-aws-programmatic-access-test-object.csv', report_file_name)

    # Process and analyze the report data using Pandas or other data analysis libraries
    df = pd.read_csv(report_file_name)

    # Example: Calculate total cost for the IAM user
    total_cost = df['lineItem/BlendedCost'].sum()
    print(f"IAM User: {user}, Total Cost: ${total_cost:.2f}")

    # Optionally, you can delete the downloaded report file
    os.remove(report_file_name)
