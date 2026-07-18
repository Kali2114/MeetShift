variable "aws_region" {
  description = "AWS region used for MeetShift infrastructure."
  type        = string
  default     = "eu-central-1"
}

variable "instance_type" {
  description = "EC2 instance type for MeetShift."
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID used by the MeetShift EC2 instance."
  type        = string
}

variable "key_name" {
  description = "Existing AWS EC2 key pair name."
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to connect to EC2 over SSH."
  type        = string
}
