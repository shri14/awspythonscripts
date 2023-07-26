import boto3
import random
import string
import json
import csv
import pandas as pd
from iam_api import app
import pymongo

def read_user_data_from_csv(csv_file):
    user_data = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_data.append(row)
    return user_data


def create_iam_user(user_name):
    iam_client = boto3.client('iam')

    try:
        response = iam_client.create_user(UserName=user_name)
        print(f"User '{user_name}' created successfully.")
        return response['User']['UserName']
    except Exception as e:
        print(f"Failed to create user '{user_name}': {e}")
        return None

def add_user_to_group(user_name, group_name):
    iam_client = boto3.client('iam')
    try:
        iam_client.add_user_to_group(UserName=user_name, GroupName=group_name)
        print(f"User '{user_name}' added to group '{group_name}' successfully.")
    except Exception as e:
        print(f"Failed to add user '{user_name}' to group '{group_name}': {e}")

def create_iam_group(group_name):
    iam_client = boto3.client('iam')
    try:
        response = iam_client.create_group(GroupName=group_name)
        print(f"Group '{group_name}' created successfully.")
        return response['Group']['GroupName']
    except Exception as e:
        print(f"Failed to create group '{group_name}': {e}")
        return None

def add_permissions(user_name, services, region):
    iam_client = boto3.client('iam')

    # Create IAM policy for the user with 'iam:ChangePassword' action only
    change_password_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "iam:ChangePassword",
                "Resource": f"arn:aws:iam::*:user/{user_name}"
            }
        ]
    }
    change_password_policy_response = iam_client.create_policy(
        PolicyName=f"{user_name}-ChangePasswordPolicy",
        PolicyDocument=json.dumps(change_password_policy_document)
    )
    iam_client.attach_user_policy(
        UserName=user_name,
        PolicyArn=change_password_policy_response['Policy']['Arn']
    )
    print(f"IAMUserChangePassword policy added to user '{user_name}' in region '{region}'.")

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(random.choice(characters) for i in range(length))
        if (any(c.isdigit() for c in password) and
                any(c in string.punctuation for c in password)):
            return password

def get_console_signin_url():
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()['Account']
    return f"https://{account_id}.signin.aws.amazon.com/console"

def main():
    herovired_group = create_iam_group("herovired")

    

   # Replace 'users.csv' with the actual name of your CSV file.
    
def read_user_data_from_csv(csv_file):
    user_data = []
    try:
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            user_name = row['name']  # Adjust the key to 'name' to match the actual column header
            group_name = row['Group']  # Assuming 'Group' is correct, keep it unchanged
            if user_name and group_name:
                user_data.append({'User': user_name, 'Group': group_name})
            else:
                print("Skipping row with missing 'name' or 'Group' data:", row)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return user_data

def main():
    herovired_group = create_iam_group("herovired")

    # Replace 'users.csv' with the actual name of your CSV file.
    user_data = read_user_data_from_csv('users.csv')

    for data in user_data:
        user = data['User']
        group = data['Group']

        user_created = create_iam_user(user)

        if user_created:
            add_user_to_group(user, group)
            add_permissions(user, [], 'us-east-1')  # Empty services list as no additional permissions needed
            temporary_password = generate_random_password()
            iam_client = boto3.client('iam')
            iam_client.create_login_profile(
                UserName=user,
                Password=temporary_password,
                PasswordResetRequired=True
            )
            console_signin_url = get_console_signin_url()
            print(f"User '{user}' Console sign-in URL: {console_signin_url}")
            print(f"Username: {user}")
            print(f"Temporary Password: {temporary_password}")

            
            # Store IAM user data in MongoDB through the API
            response = app.test_client().get('/iam_users')  # Fetch IAM users from the API
            iam_users = response.json
            if iam_users:
                iam_users.append(data)
            else:
                iam_users = [data]
            app.test_client().put('/iam_users', json=iam_users)  # Store updated IAM users through the API
            
if __name__ == "__main__":
    main()