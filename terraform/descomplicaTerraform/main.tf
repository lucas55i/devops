// Providers
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}
variable "aws_region" {
  type        = string
  description = "The region in which the resources will be created"
  default     = "us-east-1"
}

provider "aws" {
  region = var.aws_region
}
terraform {
  backend "s3" {
    bucket = "descomplica-terraform-lucasjs-1"
    key    = "terraform-test.tfstate"
    region = "us-east-1"
  }
}
