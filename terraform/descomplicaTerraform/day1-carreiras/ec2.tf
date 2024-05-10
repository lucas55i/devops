# data "aws_ami" "ubuntu" {
#   most_recent = true

#   filter {
#     name   = "name"
#     values = ["IaaSWeek-${var.hash_commit}"]
#   }

#   owners = ["019115526326"] 
# }

resource "aws_instance" "web" {
  ami           = "ami-0885b1f6bd170450c"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}
# 1

# resource "aws_instance" "web" {
#   ami           = data.aws_ami.ubuntu.id
#   instance_type = "t2.micro"

#   tags = {
#     Name = "HelloWorld"
#   }
# }
