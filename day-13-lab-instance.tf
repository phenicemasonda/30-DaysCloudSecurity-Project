# --- Provider ---
provider "aws" {
  region = var.aws_region
}

# --- Data Sources for Existing VPC, Subnet, and Security Group ---
data "aws_vpc" "lab_vpc" {
  id = "vpc-0cd710e5624398988"
}

data "aws_subnet" "lab_subnet" {
  id = "subnet-005de87c9d08605df"
}

data "aws_security_group" "lab_sg" {
  id = "sg-06e8c211193dd3e91"
}

# --- IAM Instance Profile (using existing IAM role) ---
resource "aws_iam_instance_profile" "lab_profile" {
  name = "lab-test-server-profile"
  role = "lab-test-server-role"
}

# --- Secrets Manager Secret ---
resource "aws_secretsmanager_secret" "lab_secret" {
  name        = "lab-test-secret"
  description = "Secret for testing Terraform injection"
}

# --- Secret Value ---
resource "aws_secretsmanager_secret_version" "lab_secret_value" {
  secret_id     = aws_secretsmanager_secret.lab_secret.id
  secret_string = "SuperSecretPassword123!"
}

# --- EC2 Instance ---
resource "aws_instance" "lab_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_pair_name

  subnet_id              = data.aws_subnet.lab_subnet.id
  vpc_security_group_ids = [data.aws_security_group.lab_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.lab_profile.name

  associate_public_ip_address = true

  root_block_device {
    volume_size = 8
    encrypted   = true
  }

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  # Inject secret into instance via user data
  user_data = <<-EOF
              #!/bin/bash
              echo "Injecting secret from Terraform..." >> /var/log/secret_injection.log
              echo "${aws_secretsmanager_secret_version.lab_secret_value.secret_string}" > /home/ec2-user/secret.txt
              chmod 600 /home/ec2-user/secret.txt
              EOF

  tags = {
    Name   = "LabTestSecretServer"
    VPC    = "lab-test-new-vpc"
    Subnet = "lab-test-public-sub-new"
    SG     = "lab-test-new-SG"
  }
}
