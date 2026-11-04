# EXEMPLO ILUSTRATIVO: um bucket S3 que poderia guardar exportações de extratos da
# mini-conta-digital. A API em si não usa este bucket. Serve para praticar Terraform.

provider "aws" {
  region = var.aws_region

  # Tags aplicadas automaticamente em todo recurso criado por este provider.
  default_tags {
    tags = {
      Project     = "mini-conta-digital"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

resource "aws_s3_bucket" "statements" {
  bucket = var.bucket_name
}

# Nenhum acesso público, nunca. Dados financeiros não devem ficar expostos.
resource "aws_s3_bucket_public_access_block" "statements" {
  bucket = aws_s3_bucket.statements.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versionamento: sobrescrever ou apagar um arquivo por engano não perde o original.
resource "aws_s3_bucket_versioning" "statements" {
  bucket = aws_s3_bucket.statements.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Criptografia em repouso (AES-256, chaves gerenciadas pela AWS).
resource "aws_s3_bucket_server_side_encryption_configuration" "statements" {
  bucket = aws_s3_bucket.statements.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
