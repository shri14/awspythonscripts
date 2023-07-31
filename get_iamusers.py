from flask import Flask, jsonify
import boto3
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client['iam_data']
user_collection = db['users']

def get_iam_user_list():
    iam_client = boto3.client('iam')

    try:
        response = iam_client.list_users()
        user_list = [user['UserName'] for user in response['Users']]
        return user_list
    except Exception as e:
        print(f"Error listing IAM users: {e}")
        return []

def get_iam_user_groups(username):
    iam_client = boto3.client('iam')

    try:
        response = iam_client.list_groups_for_user(UserName=username)
        group_list = [group['GroupName'] for group in response['Groups']]
        return group_list
    except Exception as e:
        print(f"Error listing IAM groups for user '{username}': {e}")
        return []

def get_account_status():
    # Implement the logic to get the account status based on your requirements
    return "Active"  # Replace this with your actual account status implementation

def main():
    # Get IAM user list
    user_list = get_iam_user_list()
    print("IAM User List:")
    print(user_list)

    # Get IAM groups for a specific user
    username = "your_username_here"  # Replace this with the IAM username you want to query
    group_list = get_iam_user_groups(username)
    print(f"IAM Groups for user '{username}':")
    print(group_list)

    # You can set the AWS region programmatically or use the default region
    region = "us-east-1"
    print(f"AWS Region: {region}")

    # Get account status
    account_status = get_account_status()
    print(f"Account Status: {account_status}")

@app.route('/iam_users', methods=['GET'])
def get_all_iam_users():
    users = get_iam_user_list()
    return jsonify(users)

@app.route('/iam_users/<username>', methods=['GET'])
def get_iam_user_by_username(username):
    groups = get_iam_user_groups(username)
    region = "us-east-1"
    account_status = get_account_status()

    user_data = {
        'Username': username,
        'Groups': groups,
        'Region': region,
        'AccountStatus': account_status,
        'Timestamp': datetime.now()
    }

    # Store the user data in MongoDB
    user_collection.insert_one(user_data)

    return jsonify(user_data)

if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=5000)
