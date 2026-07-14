resource "aws_security_group" "meetshift" {
  name        = "launch-wizard-1"
  description = "launch-wizard-1 created 2026-07-01T12:59:25.615Z"
  vpc_id      = "vpc-0129b60b0493dc894"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "launch-wizard-1"
    Project = "MeetShift"
  }
}

resource "aws_instance" "meetshift" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.meetshift.id]

  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name    = "meetshift"
    Project = "MeetShift"
  }
}

resource "aws_eip" "meetshift" {
  domain   = "vpc"
  instance = aws_instance.meetshift.id

  tags = {
    Name    = "meetshift"
    Project = "MeetShift"
  }
}
