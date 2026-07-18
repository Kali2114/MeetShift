output "instance_id" {
  description = "MeetShift EC2 instance ID."
  value       = aws_instance.meetshift.id
}

output "public_ip" {
  description = "MeetShift Elastic IP address."
  value       = aws_eip.meetshift.public_ip
}

output "public_dns" {
  description = "MeetShift EC2 public DNS name."
  value       = aws_instance.meetshift.public_dns
}
