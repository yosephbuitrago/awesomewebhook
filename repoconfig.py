from hmac import HMAC, compare_digest
from hashlib import sha256


def cofigure_repo(request, github_client, webhook_secret, logger):
    if not request.method == 'POST':
        return {'message', 'Method not allow'}, 405

    if request.headers['Content-Type'] != 'application/json':
        return {'message', 'Invalid content type. Allowed type is application/json'}, 415

    if "X-Hub-Signature-256" in request.headers and not webhook_secret:
        logger.error("Environment variable WEBHOOK_SECRET missing")
        return {'message': 'Server error'}, 500

    received_sign = request.headers.get('X-Hub-Signature-256').split('sha256=')[-1].strip()
    request_payload = request.data
    
    if not validate_signature(received_sign, request_payload, webhook_secret):
        return {'message': 'Invalid authentication'}, 401

    return setup_repo_config(request.json, github_client, logger)


def validate_signature(received_sign, request_payload, webhook_secret):
    secret = webhook_secret.encode()
    expected_sign = HMAC(key=secret, msg=request_payload, digestmod=sha256).hexdigest()
    return compare_digest(received_sign, expected_sign)

def setup_repo_config(event, github_client, logger):
    if event['action'] == "created":
        repo = github_client.get_repo(event["repository"]["full_name"])
        if repo.get_branches().totalCount == 0:
            repo.create_file("README.md", "first commit", "test")
        
        org_plan = github_client.get_organization(login=event['organization']['login']).plan.name
        
        if event["repository"]["visibility"] == "private" and org_plan == 'free':
            issue_body='''
            Confirmation of repository created and configured, 
            Unable to set branch protections for a private repo need upgrade to GitHub Pro @'''+github_client.get_user().login
            repo.create_issue(title="New repo created", body=issue_body)
            return {'message': "Repo configured"}, 200
        
        repo.get_branch('main').edit_protection(enforce_admins=True,required_approving_review_count=3,require_code_owner_reviews=True)
        issue_body='''
        Confirmation for respository created and configured, settings:
        Require a pull request before merging,
        Require approvals 3,
        Require review from Code Owners,
        Include administrators
        @'''+github_client.get_user().login
        repo.create_issue(title="New repo created", body=issue_body)
        return {'message': "Repo configured"}, 200

    elif event['action'] == "deleted":
        return {'message': 'Not action taken'}, 200
    else:
        return {'message': 'Action not implemented'}, 200



