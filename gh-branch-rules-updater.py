"""
    Script to update default protections rules using graphql API on a specific org
"""

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
import os


def main(gh_token, reviewers_count):
    # Create a transport for graphql client
    transport = AIOHTTPTransport(
        url="https://api.github.com/graphql",
        headers={'Authorization':  'bearer '+gh_token}
    )

    # Create a GraphQL client
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Query to get protections rules IDs
    repos_query = gql(
    """
    query ($numRepos: Int!, $cursor: String){ 
        viewer {
        organization(login:"YosephLab") {
        repositories(privacy:PUBLIC, first:$numRepos ,after:$cursor) {
            pageInfo {
            endCursor
            startCursor
            }
            edges {
            node {
                id
                name
                defaultBranchRef {
                branchProtectionRule {
                    id
                }
                }
            }
            }
        }
        }
    }
    }
    """
    )

    # Mutation to update the branch protection rules
    protection_mutation = gql(
    """
    mutation($Id: ID!, $reviewers_count: Int!){
        updateBranchProtectionRule(input : { branchProtectionRuleId: $Id ,requiredApprovingReviewCount: $reviewers_count, requiresCodeOwnerReviews: false }) {
            branchProtectionRule{
                id
                requiredApprovingReviewCount
                isAdminEnforced
                requiresCodeOwnerReviews
            }
        }
    }
    """
    )

    cursor = None
    # Pagination for repositories
    while True:
        result = client.execute(repos_query, variable_values={'numRepos':2, 'cursor':cursor})
        cursor = result['viewer']['organization']['repositories']['pageInfo']['endCursor']
        edges = result['viewer']['organization']['repositories']['edges']
        # Mutate protection rules for this page
        for repo in edges:
            branch_protection_rule = repo['node']['defaultBranchRef']['branchProtectionRule']['id']
            updated_rules = client.execute(protection_mutation, variable_values={"Id":branch_protection_rule, 'reviewers_count': reviewers_count})
            print(repo['node']['name'])
            print(updated_rules)
        if cursor == None:
            break


if __name__ == '__main__':
    gh_token = os.environ['GITHUB_TOKEN']
    reviewers_count = os.getenv('REVIEWERS_COUNT', 2)
    main(gh_token, reviewers_count)
  