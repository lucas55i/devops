resource "aws_internet_gateway" "eks_gw" {
  vpc_id = aws_vpc.eks_vpc.id
  tags = merge(
    var.tags,
    {
    Name = "${var.project_name}-igw" }
  )
}

resource "aws_route_table" "eks_public_route_table" {
  vpc_id = aws_vpc.eks_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.eks_gw.id
  }
  tags = merge(
    var.tags,
    {
    Name = "${var.project_name}-pub-route-table" }
  )
}