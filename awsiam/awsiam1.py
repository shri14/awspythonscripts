import boto3

# Initialize the IAM client
iam = boto3.client('iam')

def list_iam_users():
    response = iam.list_users()
    users = response['Users']
    
    for user in users:
        print("Username:", user['UserName'])

def main():
    print("List of IAM Users:")
    list_iam_users()

if __name__ == "__main__":
    main()
