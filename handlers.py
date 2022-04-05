'''
    Handler the request from GitHub
'''

from hmac import HMAC, compare_digest
from hashlib import sha256


def handler(request, github_client, webhook_secret, logger):
    '''
        Process the webhook request, validate request method, content-type and
        signature and return appropiated response based on event action
        args
        request: http request
        github_client: the github client
        webhook_secret: the secret configure in the webhook 
        logger: flask logger to log errors
    '''
    if not request.method == 'POST':
        return {'message', 'Method not allow'}, 405

    if request.headers['Content-Type'] != 'application/json':
        return {
            'message', 'Invalid content type. Allowed type is application/json'
        }, 415

    if "X-Hub-Signature-256" in request.headers and not webhook_secret:
        logger.error("Environment variable WEBHOOK_SECRET missing")
        return {'message': 'Server error'}, 500

    received_sign = request.headers.get('X-Hub-Signature-256').split(
        'sha256=')[-1].strip()
    request_payload = request.data

    if not validate_signature(received_sign, request_payload, webhook_secret):
        return {'message': 'Invalid authentication'}, 401

    return setup_repo_config(request.json, github_client)


def validate_signature(received_sign, request_payload, webhook_secret):
    '''
        Validate the signature given
        args:
        received_sign: signature to validate
        request_payload: request payload to compute the signature
        webhook_secret: secret to perform the HMAC operation
    '''
    secret = webhook_secret.encode()
    expected_sign = HMAC(key=secret, msg=request_payload,
                         digestmod=sha256).hexdigest()
    return compare_digest(received_sign, expected_sign)


def setup_repo_config(event, github_client):
    '''
        Perform appropiate branch configuration based on event action
        args
        event: github event 
        github_client: Github Client to perform APIs call
    '''
    # handle the initial webhook config
    if 'zen' in event and 'hook_id' in event:
        return {'message': 'webhook ready for work!'}

    if event['action'] == "created":

        # Get repo object that trigger the event
        repo = github_client.get_repo(event["repository"]["full_name"])

        # Check if the repo was created with README.md or .gitignore options
        # If not creates the default README.md file
        path = "README.md"
        content = ":rocket: Time to build a new project. have fun :wink:!"
        if repo.get_branches().totalCount == 0:
            repo.create_file(
                path,
                "first commit",
                content
            )
        else:
            try:
                if repo.get_readme():
                    repo.update_file(
                        path,
                        "second commit",
                        content,
                        repo.get_readme().sha
                    )
            except Exception as e:
                repo.create_file(
                    path,
                    "second commit",
                    content
                )
                pass

        # Get the current organization plan.
        org_plan = github_client.get_organization(
            login=event['organization']['login']).plan.name

        # If org is free and the repo is private. We can't set branch protection
        # You need to upgrade to GitHub teams for this feature on private repos
        if event["repository"][
                "visibility"] == "private" and org_plan == 'free':

            # Create an issue with the configuration of the repo
            issue_body = '''
            Confirmation of repository created and configured, 
            Unable to set branch protections for a private repo need upgrade to GitHub Pro @''' + github_client.get_user(
            ).login
            repo.create_issue(title="New repo created", body=issue_body)
            return {'message': "Repo configured"}, 201

        # If the repo is public, edit the protection on the default branch
        repo.get_branch('main').edit_protection(
            enforce_admins=True,
            required_approving_review_count=3,
            require_code_owner_reviews=True)

        # Create an issue with the configuration of the repo
        issue_body = '''
        Confirmation for respository created and configured, settings:
        Require a pull request before merging,
        Require approvals 3,
        Require review from Code Owners,
        Include administrators
        @''' + github_client.get_user().login

        repo.create_issue(title="New repo configured", body=issue_body)
        return {'message': "Repo configured"}, 201

    elif event['action'] == "deleted":
        return {'message': 'Not action taken'}, 202
    else:
        return {'message': 'Action not implemented'}, 202
