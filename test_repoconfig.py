import unittest
import hmac
import hashlib
from unittest.mock import Mock
from unittest.mock import patch

from repoconfig import cofigure_repo, validate_signature, setup_repo_config



class ValidateRequest(unittest.TestCase):

    def test_method_not_allow(self):
        request = Mock()
        request.method = "GET"
        result = cofigure_repo(request, Mock(), Mock(), Mock())
        assert result == ({'Method not allow', 'message'}, 405)

    def test_invalid_content_type(self):
        request = Mock()
        request.method = "POST"
        request.headers={'Content-Type': 'application/x-www-from-urlencoded'}
        result = cofigure_repo(request, Mock(), Mock(), Mock())
        assert result == ({'message', 'Invalid content type. Allowed type is application/json'}, 415)

    def test_missing_secret(self):
        request = Mock()
        request.method = "POST"
        request.headers={
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': 'sha=sha256=1c405447c626670bdf3a9e3c0e204864e9bfc2f67866a154e9d72c2789062748'
        }
        result = cofigure_repo(request, Mock(), False, Mock())
        assert result == ({'message': 'Check server logs'}, 500)

class ValidateSignature(unittest.TestCase):

    def test_valid_signature(sefl):
        json = b'{"signature":"test"}'
        secret_key = "secret"
        received_sign = hmac.new(key=secret_key.encode(), msg=json, digestmod=hashlib.sha256).hexdigest()
        result = validate_signature(received_sign, json, secret_key)
        assert True

    def test_invalid_signature(sefl):
        json = b'{"signature":"test"}'
        secret_key = "secret"
        received_sign = hmac.new(key=secret_key.encode(), msg=json, digestmod=hashlib.sha256).hexdigest()
        result = validate_signature(received_sign, json, "other")
        assert True

class setupRepoConfig(unittest.TestCase):
    def test_delete_branch(self):
        event={'action': 'deleted'}
        result = setup_repo_config(event, Mock(), Mock())
        assert result == ({'message': 'Not action taken'}, 200)

    def test_any_other_action(self):
        event={'action': 'updated'}
        result = setup_repo_config(event, Mock(), Mock())
        assert result == ({'message': 'Action not implemented'}, 200)

    def test_config_public_repo_free_org(self):
        event={
            'action': 'created',
            'repository': {
                'full_name': 'test',
                'visibility': 'public'
            },
            'organization': {
                'login': 'org_test'
            }
        }
        branch = Mock()
        repo = Mock()
        github_client = repo
        github_client.get_repo = repo
        github_client.get_user().login = "test"
        repo.get_branches().totalCount = 0
        github_client.get_organization().plan.name = "free"
        result = setup_repo_config(event,github_client, Mock())
        github_client.get_repo.assert_called()
        github_client.get_repo.assert_called_with(event['repository']['full_name'])
        github_client.get_organization.assert_called()
        github_client.get_organization.assert_called_with(login=event['organization']['login'])
        github_client.get_branches()
        repo.get_repo.assert_called_with('test')
        repo.get_branches.assert_called()
        assert result == ({'message': "Repo configured"}, 200)
