output "bucket_name" {
  description = "Nome do bucket criado."
  value       = aws_s3_bucket.statements.id
}

output "bucket_arn" {
  description = "ARN (identificador único na AWS) do bucket."
  value       = aws_s3_bucket.statements.arn
}
