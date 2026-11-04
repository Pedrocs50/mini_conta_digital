variable "aws_region" {
  description = "Região da AWS onde os recursos seriam criados."
  type        = string
  default     = "sa-east-1" # São Paulo
}

variable "environment" {
  description = "Nome do ambiente (vira uma tag em todos os recursos)."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment deve ser dev, staging ou prod."
  }
}

variable "bucket_name" {
  description = "Nome do bucket S3. Precisa ser único no mundo todo, em toda a AWS."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.bucket_name))
    error_message = "bucket_name deve ter de 3 a 63 caracteres: letras minúsculas, números, ponto ou hífen."
  }
}
