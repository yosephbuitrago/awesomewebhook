import os 
from github import Github
from flask import Flask
from flask import request
from flask import json 
from repoconfig import cofigure_repo


app = Flask(__name__)
github_token = os.getenv("GITHUB_TOKEN")
github_client = Github(github_token)
webhook_secret = os.getenv("WEBHOOK_SECRET")

@app.route('/', methods=['GET'])
def index():
  return "hellooooo"

@app.route('/webhook', methods=['POST'])   
def hook_root():
  return cofigure_repo(request, github_client, webhook_secret, app.logger)


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')

