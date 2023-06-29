variable "prefix" {
  default = "taxi-p"
}

variable "project" {
  default = "taxi-project-devops"
}

variable "db_username" {
  description = "Username for the RDS Postgres instance"
}

variable "db_password" {
  description = "Password for the RDS postgres instance"
}

variable "bastion_key_name" {
  default = "taxi-project-bastion-imac"
}

variable "ecr_image_api" {
  description = "ECR Image for API"
  default     = "261112143448.dkr.ecr.ap-northeast-1.amazonaws.com/taxi-django-devops:latest"
}

variable "ecr_image_proxy" {
  description = "ECR Image for API"
  default     = "261112143448.dkr.ecr.ap-northeast-1.amazonaws.com/taxi-django-proxy:latest"
}

variable "django_secret_key" {
  description = "Secret key for Django app"
}

variable "dns_zone_name" {
  description = "Domain name"
  default     = "taxitaiwan.com"
}