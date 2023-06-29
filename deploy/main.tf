terraform {
  backend "s3" {
    bucket         = "taxi-kaoshungwu-app-devops-tfstate"
    key            = "taxi-kaoshungwu-app-devops.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    dynamodb_table = "taxi-kaoshungwu-app-devops-tf-state-lock"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
}

locals {
  prefix = var.prefix
  common_tags = {
    Project   = var.project
    ManagedBy = "terraform"
  }
}

data "aws_region" "current" {}