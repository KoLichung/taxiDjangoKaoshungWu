output "DB_HOST" {
  value = aws_db_instance.main.address
}

output "DB_NAME" {
  value = aws_db_instance.main.name
}

output "bastion_host" {
  value = aws_instance.bastion.public_dns
}

output "api_endpoint" {
  value = aws_lb.api.dns_name
}