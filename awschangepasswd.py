import boto3
import random
import string
import json

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

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def get_console_signin_url():
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()['Account']
    return f"https://{account_id}.signin.aws.amazon.com/console"

def main():
    herovired_group = create_iam_group("herovired")

    # Replace this with the desired usernames
    users = ['Tester', 'Analyst']

    for user in users:
        user_created = create_iam_user(user)

        if user_created:
            add_user_to_group(user, herovired_group)
            add_permissions(user, [], 'us-east-1')  # Empty services list as no additional permissions needed
            temporary_password = generate_random_password()
            iam_client = boto3.client('iam')
            iam_client.create_login_profile(
                UserName=user,
                Password=temporary_password,
                PasswordResetRequired=True
            )
            print(f"User '{user}' Console sign-in URL: {get_console_signin_url()}")
            print(f"Username: {user}")
            print(f"Temporary Password: {temporary_password}")

if __name__ == "__main__":
    main()
