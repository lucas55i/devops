module "eks_network" {
  source       = "./models/network"
  cidr_block   = var.cidr_block
  project_name = var.project_name
  tags         = local.tags
}

module "eks_cluster" {
  source       = "./models/cluster"
  project_name = var.project_name
  tags         = local.tags
}