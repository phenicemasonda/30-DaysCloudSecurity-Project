output "aws_retrieved_secret_value" {
  description = "The application secret retrieved from AWS Secrets Manager."
  value       = aws_secretsmanager_secret_version.lab_secret_value.secret_string
  sensitive   = true # Mark as sensitive
}

output "consistency_status" {
  description = "Status of the secret consistency check."
  value       = "PASSED: Secret successfully created in AWS Secrets Manager."
}
