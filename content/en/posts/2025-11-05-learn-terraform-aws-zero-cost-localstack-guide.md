---
title: "Learn Terraform and AWS at Zero Cost with LocalStack: A Complete Practical Guide"
date: 2025-11-05T09:00:00+08:00
slug: learn-terraform-aws-zero-cost-localstack-guide
categories: 
- Engineering
tags:
- terraform
- aws
featured: true
---

When learning AWS and Terraform, the biggest pain points are often the high costs of cloud services and the financial risks of misconfigurations. This guide will show you how to use LocalStack to simulate AWS services locally, enabling you to learn and experiment with Terraform Infrastructure as Code (IaC) at zero cost and zero risk.

In this tutorial, we'll build a complete AWS network architecture including VPC, public/private subnets, Internet Gateway, security groups, and EC2 instances. All resources run in your local LocalStack environment without incurring any AWS charges or security risks from configuration errors.

<!--more-->

> **Note**: LocalStack creates simulated AWS resources for local development and testing purposes only. While these resources cannot be accessed from external networks, this is the perfect way to learn Terraform and become familiar with AWS services without worrying about costs or security.

## Installation

+ Install Terraform: https://developer.hashicorp.com/terraform/install
+ Install Localstack: https://docs.localstack.cloud/aws/getting-started/installation/

## Launch Localstack

```bash
localstack start
```

## Build a simple architecture

We'll build a simple architecture with a VPC, a public subnet, a private subnet, an internet gateway, a route table, a route table association, a security group, and an EC2 instance.

### Terraform Code

Create a new directory for your project and navigate to it.

```bash
mkdir learn-terraform-aws-localstack
cd learn-terraform-aws-localstack
```

**provider.tf**
> This file contains the provider configuration for AWS.

```hcl
provider "aws" {
  access_key                  = "mock_access_key"
  region                      = "us-east-1"
  s3_use_path_style           = true
  secret_key                  = "mock_secret_key"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    apigateway     = "http://localhost:4566"
    cloudformation = "http://localhost:4566"
    cloudwatch     = "http://localhost:4566"
    dynamodb       = "http://localhost:4566"
    ec2            = "http://localhost:4566"
    es             = "http://localhost:4566"
    firehose       = "http://localhost:4566"
    iam            = "http://localhost:4566"
    kinesis        = "http://localhost:4566"
    lambda         = "http://localhost:4566"
    route53        = "http://localhost:4566"
    redshift       = "http://localhost:4566"
    s3             = "http://localhost:4566"
    secretsmanager = "http://localhost:4566"
    ses            = "http://localhost:4566"
    sns            = "http://localhost:4566"
    sqs            = "http://localhost:4566"
    ssm            = "http://localhost:4566"
    stepfunctions  = "http://localhost:4566"
    sts            = "http://localhost:4566"
  }
}
```

**main.tf**
> This file contains the Terraform code for our architecture.

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.workspace}-vpc"
    Workspace = var.workspace
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.workspace}-igw"
    Workspace = var.workspace
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  map_public_ip_on_launch = true
  availability_zone       = "${var.region}a"

  tags = {
    Name = "${var.workspace}-public-subnet"
    Workspace = var.workspace
  }
}

# Private Subnet
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidr
  availability_zone = "${var.region}a"

  tags = {
    Name = "${var.workspace}-private-subnet"
    Workspace = var.workspace
  }
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.workspace}-public-rt"
    Workspace = var.workspace
  }
}

# Private Route Table
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.workspace}-private-rt"
    Workspace = var.workspace
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# Security Group for EC2
resource "aws_security_group" "ec2" {
  name        = "${var.workspace}-ec2-sg"
  description = "Security group for EC2 instance"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Allow port 8000 from anywhere"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.workspace}-ec2-sg"
    Workspace = var.workspace
  }
}


# EC2 Instance in Public Subnet
resource "aws_instance" "web" {
  ami                    = var.ec2_ami
  instance_type          = var.ec2_instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ec2.id]

  tags = {
    Name = "${var.workspace}-web-server"
  }
}
```

**vars.tf**
> This file contains the variables for our architecture.

```hcl
variable "workspace" {
    type = string
    description = "The workspace to use"
    default = "dev"
}

variable "region" {
    type = string
    description = "The region to use"
    default = "us-east-1"
}

variable "vpc_cidr" {
    type = string
    description = "CIDR block for VPC"
    default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
    type = string
    description = "CIDR block for public subnet"
    default = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
    type = string
    description = "CIDR block for private subnet"
    default = "10.0.2.0/24"
}

variable "ec2_instance_type" {
    type = string
    description = "EC2 instance type"
    default = "t3.micro"
}

variable "ec2_ami" {
    type = string
    description = "AMI ID for EC2 instance"
    default = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2
}
```

**outputs.tf**
> This file contains the outputs for our architecture.

```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "Public subnet ID"
  value       = aws_subnet.public.id
}

output "private_subnet_id" {
  description = "Private subnet ID"
  value       = aws_subnet.private.id
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.web.id
}

output "ec2_public_ip" {
  description = "EC2 instance public IP"
  value       = aws_instance.web.public_ip
}

output "ec2_private_ip" {
  description = "EC2 instance private IP"
  value       = aws_instance.web.private_ip
}

output "security_group_id" {
  description = "EC2 security group ID"
  value       = aws_security_group.ec2.id
}
```

### Run Terraform

Run the following commands to build the architecture.

```bash
terraform init # This will download the provider plugins
terraform plan # This will show the changes that will be applied
terraform apply # This will apply the changes
```

Run the following command to see the whole state of the infrastructure.

```bash
terraform show
```

Here is my state:

```
# aws_instance.web:
resource "aws_instance" "web" {
    ami                                  = "ami-0c55b159cbfafe1f0"
    arn                                  = "arn:aws:ec2:us-east-1::instance/i-628f2d8a778d0398f"
    associate_public_ip_address          = true
    availability_zone                    = "us-east-1a"
    disable_api_stop                     = false
    disable_api_termination              = false
    ebs_optimized                        = false
    force_destroy                        = false
    get_password_data                    = false
    hibernation                          = false
    host_id                              = null
    iam_instance_profile                 = "dev-ec2-profile"
    id                                   = "i-628f2d8a778d0398f"
    instance_initiated_shutdown_behavior = "stop"
    instance_lifecycle                   = null
    instance_state                       = "running"
    instance_type                        = "t3.micro"
    ipv6_address_count                   = 0
    ipv6_addresses                       = []
    key_name                             = null
    monitoring                           = false
    outpost_arn                          = null
    password_data                        = null
    placement_group                      = null
    placement_group_id                   = null
    placement_partition_number           = 0
    primary_network_interface_id         = "eni-a320bc52a3f9cc681"
    private_dns                          = "ip-10-0-1-4.ec2.internal"
    private_ip                           = "10.0.1.4"
    public_dns                           = "ec2-54-214-147-137.compute-1.amazonaws.com"
    public_ip                            = "54.214.147.137"
    region                               = "us-east-1"
    secondary_private_ips                = []
    security_groups                      = []
    source_dest_check                    = true
    spot_instance_request_id             = null
    subnet_id                            = "subnet-296cb609d6cf6c00c"
    tags                                 = {
        "Name" = "dev-web-server"
    }
    tags_all                             = {
        "Name" = "dev-web-server"
    }
    tenancy                              = "default"
    user_data_replace_on_change          = false
    vpc_security_group_ids               = [
        "sg-6dac1e4483215e7cd",
    ]

    metadata_options {
        http_endpoint               = "enabled"
        http_protocol_ipv6          = "disabled"
        http_put_response_hop_limit = 1
        http_tokens                 = "optional"
        instance_metadata_tags      = "disabled"
    }

    primary_network_interface {
        delete_on_termination = true
        network_interface_id  = "eni-a320bc52a3f9cc681"
    }

    root_block_device {
        delete_on_termination = true
        device_name           = "/dev/sda1"
        encrypted             = false
        iops                  = 0
        kms_key_id            = null
        tags                  = {}
        tags_all              = {}
        throughput            = 0
        volume_id             = "vol-863def1230da5eec3"
        volume_size           = 8
        volume_type           = "gp2"
    }
}

# aws_internet_gateway.main:
resource "aws_internet_gateway" "main" {
    arn      = "arn:aws:ec2:us-east-1:000000000000:internet-gateway/igw-2b2b955804ed3852f"
    id       = "igw-2b2b955804ed3852f"
    owner_id = "000000000000"
    region   = "us-east-1"
    tags     = {
        "Name"      = "dev-igw"
        "Workspace" = "dev"
    }
    tags_all = {
        "Name"      = "dev-igw"
        "Workspace" = "dev"
    }
    vpc_id   = "vpc-1f5d8418e1e2ce4dc"
}

# aws_route_table.private:
resource "aws_route_table" "private" {
    arn              = "arn:aws:ec2:us-east-1:000000000000:route-table/rtb-f33ee41ac3ddc20d0"
    id               = "rtb-f33ee41ac3ddc20d0"
    owner_id         = "000000000000"
    propagating_vgws = []
    region           = "us-east-1"
    route            = []
    tags             = {
        "Name"      = "dev-private-rt"
        "Workspace" = "dev"
    }
    tags_all         = {
        "Name"      = "dev-private-rt"
        "Workspace" = "dev"
    }
    vpc_id           = "vpc-1f5d8418e1e2ce4dc"
}

# aws_route_table.public:
resource "aws_route_table" "public" {
    arn              = "arn:aws:ec2:us-east-1:000000000000:route-table/rtb-d5f6d58f5ad703b08"
    id               = "rtb-d5f6d58f5ad703b08"
    owner_id         = "000000000000"
    propagating_vgws = []
    region           = "us-east-1"
    route            = [
        {
            carrier_gateway_id         = null
            cidr_block                 = "0.0.0.0/0"
            core_network_arn           = null
            destination_prefix_list_id = null
            egress_only_gateway_id     = null
            gateway_id                 = "igw-2b2b955804ed3852f"
            ipv6_cidr_block            = null
            local_gateway_id           = null
            nat_gateway_id             = null
            network_interface_id       = null
            transit_gateway_id         = null
            vpc_endpoint_id            = null
            vpc_peering_connection_id  = null
        },
    ]
    tags             = {
        "Name"      = "dev-public-rt"
        "Workspace" = "dev"
    }
    tags_all         = {
        "Name"      = "dev-public-rt"
        "Workspace" = "dev"
    }
    vpc_id           = "vpc-1f5d8418e1e2ce4dc"
}

# aws_route_table_association.private:
resource "aws_route_table_association" "private" {
    gateway_id     = null
    id             = "rtbassoc-084a1cbcbcbe6e0c5"
    region         = "us-east-1"
    route_table_id = "rtb-f33ee41ac3ddc20d0"
    subnet_id      = "subnet-489196b43b007d2db"
}

# aws_route_table_association.public:
resource "aws_route_table_association" "public" {
    gateway_id     = null
    id             = "rtbassoc-b0f38c2456e2fef35"
    region         = "us-east-1"
    route_table_id = "rtb-d5f6d58f5ad703b08"
    subnet_id      = "subnet-296cb609d6cf6c00c"
}

# aws_security_group.ec2:
resource "aws_security_group" "ec2" {
    arn                    = "arn:aws:ec2:us-east-1:000000000000:security-group/sg-6dac1e4483215e7cd"
    description            = "Security group for EC2 instance"
    egress                 = [
        {
            cidr_blocks      = [
                "0.0.0.0/0",
            ]
            description      = "Allow all outbound traffic"
            from_port        = 0
            ipv6_cidr_blocks = []
            prefix_list_ids  = []
            protocol         = "-1"
            security_groups  = []
            self             = false
            to_port          = 0
        },
    ]
    id                     = "sg-6dac1e4483215e7cd"
    ingress                = [
        {
            cidr_blocks      = [
                "0.0.0.0/0",
            ]
            description      = "Allow port 8000 from anywhere"
            from_port        = 8000
            ipv6_cidr_blocks = []
            prefix_list_ids  = []
            protocol         = "tcp"
            security_groups  = []
            self             = false
            to_port          = 8000
        },
    ]
    name                   = "dev-ec2-sg"
    name_prefix            = null
    owner_id               = "000000000000"
    region                 = "us-east-1"
    revoke_rules_on_delete = false
    tags                   = {
        "Name"      = "dev-ec2-sg"
        "Workspace" = "dev"
    }
    tags_all               = {
        "Name"      = "dev-ec2-sg"
        "Workspace" = "dev"
    }
    vpc_id                 = "vpc-1f5d8418e1e2ce4dc"
}

# aws_subnet.private:
resource "aws_subnet" "private" {
    arn                                            = "arn:aws:ec2:us-east-1:000000000000:subnet/subnet-489196b43b007d2db"
    assign_ipv6_address_on_creation                = false
    availability_zone                              = "us-east-1a"
    availability_zone_id                           = "use1-az6"
    cidr_block                                     = "10.0.2.0/24"
    customer_owned_ipv4_pool                       = null
    enable_dns64                                   = false
    enable_lni_at_device_index                     = 0
    enable_resource_name_dns_a_record_on_launch    = false
    enable_resource_name_dns_aaaa_record_on_launch = false
    id                                             = "subnet-489196b43b007d2db"
    ipv6_cidr_block                                = null
    ipv6_cidr_block_association_id                 = null
    ipv6_native                                    = false
    map_customer_owned_ip_on_launch                = false
    map_public_ip_on_launch                        = false
    outpost_arn                                    = null
    owner_id                                       = "000000000000"
    private_dns_hostname_type_on_launch            = "ip-name"
    region                                         = "us-east-1"
    tags                                           = {
        "Name"      = "dev-private-subnet"
        "Workspace" = "dev"
    }
    tags_all                                       = {
        "Name"      = "dev-private-subnet"
        "Workspace" = "dev"
    }
    vpc_id                                         = "vpc-1f5d8418e1e2ce4dc"
}

# aws_subnet.public:
resource "aws_subnet" "public" {
    arn                                            = "arn:aws:ec2:us-east-1:000000000000:subnet/subnet-296cb609d6cf6c00c"
    assign_ipv6_address_on_creation                = false
    availability_zone                              = "us-east-1a"
    availability_zone_id                           = "use1-az6"
    cidr_block                                     = "10.0.1.0/24"
    customer_owned_ipv4_pool                       = null
    enable_dns64                                   = false
    enable_lni_at_device_index                     = 0
    enable_resource_name_dns_a_record_on_launch    = false
    enable_resource_name_dns_aaaa_record_on_launch = false
    id                                             = "subnet-296cb609d6cf6c00c"
    ipv6_cidr_block                                = null
    ipv6_cidr_block_association_id                 = null
    ipv6_native                                    = false
    map_customer_owned_ip_on_launch                = false
    map_public_ip_on_launch                        = true
    outpost_arn                                    = null
    owner_id                                       = "000000000000"
    private_dns_hostname_type_on_launch            = "ip-name"
    region                                         = "us-east-1"
    tags                                           = {
        "Name"      = "dev-public-subnet"
        "Workspace" = "dev"
    }
    tags_all                                       = {
        "Name"      = "dev-public-subnet"
        "Workspace" = "dev"
    }
    vpc_id                                         = "vpc-1f5d8418e1e2ce4dc"
}

# aws_vpc.main:
resource "aws_vpc" "main" {
    arn                                  = "arn:aws:ec2:us-east-1:000000000000:vpc/vpc-1f5d8418e1e2ce4dc"
    assign_generated_ipv6_cidr_block     = false
    cidr_block                           = "10.0.0.0/16"
    default_network_acl_id               = "acl-89a71b82683d7254b"
    default_route_table_id               = "rtb-0fcd2ecf27bae8732"
    default_security_group_id            = "sg-f10b7fa4f906a9ef4"
    dhcp_options_id                      = "default"
    enable_dns_hostnames                 = true
    enable_dns_support                   = true
    enable_network_address_usage_metrics = false
    id                                   = "vpc-1f5d8418e1e2ce4dc"
    instance_tenancy                     = "default"
    ipv6_association_id                  = null
    ipv6_cidr_block                      = null
    ipv6_cidr_block_network_border_group = null
    ipv6_ipam_pool_id                    = null
    ipv6_netmask_length                  = 0
    main_route_table_id                  = "rtb-0fcd2ecf27bae8732"
    owner_id                             = "000000000000"
    region                               = "us-east-1"
    tags                                 = {
        "Name"      = "dev-vpc"
        "Workspace" = "dev"
    }
    tags_all                             = {
        "Name"      = "dev-vpc"
        "Workspace" = "dev"
    }
}


Outputs:

ec2_instance_id = "i-628f2d8a778d0398f"
ec2_private_ip = "10.0.1.4"
ec2_public_ip = "54.214.147.137"
private_subnet_id = "subnet-489196b43b007d2db"
public_subnet_id = "subnet-296cb609d6cf6c00c"
security_group_id = "sg-6dac1e4483215e7cd"
vpc_id = "vpc-1f5d8418e1e2ce4dc"
```

### Clean up

```bash
terraform destroy # This will destroy the infrastructure
```