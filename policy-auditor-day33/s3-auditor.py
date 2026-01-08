import boto3
import json

def analyze_policy(policy_name, version_doc):
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
                    finding["Remediation"] = "CRITICAL: Full Admin Access. Replace with specific service actions (e.g., 's3:GetObject')."
                else:
                    finding["Remediation"] = f"Narrow scope from '{', '.join(prefixes)}:*' to specific required APIs."
            if has_resource_wildcard:
                finding["Remediation"] += " Replace '*' with specific bucket ARNs to restrict resource access."
            findings.append(finding)

    return findings

def main():
    s3 = boto3.client('s3', region_name='af-south-1')
    buckets = s3.list_buckets()['Buckets']
    print(f"{'Bucket Name':<40} | {'Status':<10}")
    print("-" * 55)

    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            policy_str = s3.get_bucket_policy(Bucket=bucket_name)['Policy']
            policy_doc = json.loads(policy_str)
            findings = analyze_policy(bucket_name, policy_doc)

            if findings:
                print(f"{bucket_name:<40} | RISKY")
                for f in findings:
                    print(f"  - Statement {f['StatementIndex']}: Found {f['RiskyActions']} on {f['RiskyResources']}")
                    print(f"     Suggestion: {f['Remediation']}")
            else:
                print(f"{bucket_name:<40} | SECURE")
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                print(f"{bucket_name:<40} | NO POLICY")
            else:
                print(f"{bucket_name:<40} | ERROR")

if __name__ == "__main__":
    main()
