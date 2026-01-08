import boto3
import json

def analyze_policy(policy_name, version_doc):
    """
    Analyzes a policy document for wildcards and suggests remediations.
    """
    findings = []
    statements = version_doc.get('Statement', [])
    
    
    if isinstance(statements, dict):
        statements = [statements]

    for i, stmt in enumerate(statements):
        if stmt.get('Effect') == 'Deny':
            continue

        actions = stmt.get('Action', [])
        resources = stmt.get('Resource', [])

        
        if isinstance(actions, str): actions = [actions]
        if isinstance(resources, str): resources = [resources]

        
        has_action_wildcard = any("*" in a for a in actions)
        has_resource_wildcard = any("*" in r for r in resources)

        if has_action_wildcard or has_resource_wildcard:
            finding = {
                "StatementIndex": i,
                "RiskyActions": [a for a in actions if "*" in a],
                "RiskyResources": [r for r in resources if "*" in r],
                "Remediation": ""
            }

            
            if has_action_wildcard:
                
                prefixes = set([a.split(':')[0] for a in actions if ":" in a])
                if not prefixes and "*" in actions:
                    finding["Remediation"] = "CRITICAL: Full Admin Access. Replace with specific service actions (e.g., 'ec2:Describe*')."
                else:
                    finding["Remediation"] = f"Narrow scope from '{', '.join(prefixes)}:*' to specific required APIs."
            
            if has_resource_wildcard:
                finding["Remediation"] += " Replace '*' with specific ARNs to restrict resource access."
            
            findings.append(finding)

    return findings

def main():
    iam = boto3.client('iam')
    print(f"{'Policy Name':<40} | {'Status':<10}")
    print("-" * 55)

    
    paginator = iam.get_paginator('list_policies')
    for page in paginator.paginate(Scope='Local', OnlyAttached=True):
        for policy in page['Policies']:
            policy_arn = policy['Arn']
            policy_name = policy['PolicyName']
            
            
            version = iam.get_policy_version(
                PolicyArn=policy_arn,
                VersionId=policy['DefaultVersionId']
            )
            policy_doc = version['Document']
            
            findings = analyze_policy(policy_name, policy_doc)

            if findings:
                print(f"{policy_name:<40} | RISKY")
                for f in findings:
                    print(f"  - Statement {f['StatementIndex']}: Found {f['RiskyActions']} on {f['RiskyResources']}")
                    print(f"     Suggestion: {f['Remediation']}")
            else:
                print(f"{policy_name:<40} |  SECURE")

if __name__ == "__main__":
    main()
