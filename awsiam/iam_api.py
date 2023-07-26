from flask import Flask, jsonify
import pymongo

app = Flask(__name__)

# Establish a connection to MongoDB
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["mydatabase"]  # Replace "mydatabase" with the name of your MongoDB database
collection = db["iam_users"]     # Replace "iam_users" with the name of the collection where you store IAM user data

@app.route('/iam_users', methods=['GET'])
def get_iam_users():
    # Fetch the IAM users from MongoDB and return as JSON.
    users = list(collection.find({}, {'_id': 0}))
    return jsonify(users)

if __name__ == "__main__":
    app.run()