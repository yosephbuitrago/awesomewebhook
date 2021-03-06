'''
  Create a basic Flask web app that listen on port 5000
  in the main root for POST request
'''
import os
from github import Github
from flask import Flask
from flask import request
from flask import json
from handlers import handler

# Create the flask app and get environmemt variables need it
app = Flask(__name__)
github_token = os.getenv("GITHUB_TOKEN")
github_client = Github(github_token)
webhook_secret = os.getenv("WEBHOOK_SECRET")


@app.route('/', methods=['POST'])
def hook_root():
    '''
    Creates the endpoint that listen for POST request
    '''
    return handler(request, github_client, webhook_secret, app.logger)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
