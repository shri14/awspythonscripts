import boto3
import datetime

# Initialize AWS services
ce = boto3.client('ce', region_name='ap-south-1')  # Specify your AWS region
iam = boto3.client('iam')

# Specify the IAM group name you want to check
group_name = 'herovired'

# Get the list of IAM users in the group
response = iam.get_group(GroupName=group_name)
users_in_group = response['Users']

# Define the start and end dates for the analysis (September 1st to 30th, 2023)
start_date = '2023-09-01'
end_date = '2023-09-30'

# List of metrics to check (in order of preference)
metrics_to_check = ['UnblendedCost', 'AmortizedCost', 'BlendedCost']

# Initialize dictionaries to store cost data
root_bill = 0.0
user_costs = {}

# Get the root account's billing information for the specified time period
try:
    results = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='DAILY',
        Metrics=metrics_to_check,
        Filter={
            'Dimensions': {
                'Key': 'LINKED_ACCOUNT',
                'Values': ['295397358094']  # Replace with your AWS Account ID
            }
        }
    )

    # Calculate the total cost for the root account if available
    if 'ResultsByTime' in results:
        total_cost = 0
        for result in results.get('ResultsByTime', []):
            total_cost += float(result.get('Total', {}).get('UnblendedCost', {}).get('Amount', 0))

        root_bill = total_cost
except Exception as e:
    pass

# Iterate through IAM users in the group
for user in users_in_group:
    username = user['UserName']
    account_id = user['Arn'].split(":")[4]
    
    # Get each IAM user's billing information for the specified time period
    try:
        results = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=metrics_to_check,
            Filter={
                'Dimensions': {
                    'Key': 'LINKED_ACCOUNT',
                    'Values': [account_id]
                }
            }
        )

        # Calculate the total cost for the user if available
        if 'ResultsByTime' in results:
            total_cost = 0
            for result in results.get('ResultsByTime', []):
                total_cost += float(result.get('Total', {}).get('UnblendedCost', {}).get('Amount', 0))

            user_costs[username] = total_cost
    except Exception as e:
        pass

# Print the root account bill
print(f"Root Account Bill: ${root_bill:.2f}")

# Print the cost utilization for each IAM user
for username, cost in user_costs.items():
    print(f"IAM User: {username}")
    print(f"IAM User Cost: ${cost:.2f}")
