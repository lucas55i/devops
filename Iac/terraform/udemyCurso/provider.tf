terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.0.0-beta1"
    }
  }
  backend "s3" {
    bucket = "comunidadedevops-lpzeus"
    key    = "dev/terraforma.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  # Configuration options
  region = "us-east-1"
}