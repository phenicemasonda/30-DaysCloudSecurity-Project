provider "aws" {
  region = "af-south-1"
}


resource "aws_s3_bucket" "test_buckets" {
  count  = 3
  bucket = "vulnerable-test-bucket-${count.index}"
}


resource "aws_s3_bucket_public_access_block" "disable_block" {
  count                   = 3
  bucket                  = aws_s3_bucket.test_buckets[count.index].id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}


resource "aws_s3_bucket_policy" "bad_policy" {
  count  = 3
  bucket = aws_s3_bucket.test_buckets[count.index].id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BadPolicyWildcard",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "*",
      "Resource": [
        "arn:aws:s3:::${aws_s3_bucket.test_buckets[count.index].id}",
        "arn:aws:s3:::${aws_s3_bucket.test_buckets[count.index].id}/*"
      ]
    }
  ]
}
POLICY

  
  depends_on = [aws_s3_bucket_public_access_block.disable_block]
}
