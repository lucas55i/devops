// Resources
resource "aws_cognito_user_pool" "user_pool" {
  name                     = "user-pool-terraform-dev-lucas" # Alterar para o nome do cliente que está sendo implantado ex: client_user_pool
  alias_attributes         = ["preferred_username"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "Account Confirmation"
    email_message        = "Your confirmation code is {####}"
  }

  schema {
    name                     = "email"
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    required                 = true
    string_attribute_constraints {
      min_length = 1
      max_length = 50
    }
  }

  schema {
    name                     = "email"
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    required                 = true
    string_attribute_constraints {
      min_length = 1
      max_length = 50
    }
  }

  tags = {
    author      = "lucasdscdje@algartech.com" # Alterar para o nome de quem está  implantando
    customer    = "Terraform Teste "          # Alterar para o nome do cliente que está sendo implantado
    environment = "dev"                       # dev ou prod
    project     = "wit5"
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "admin_only"
      priority = 1
    }
  }

  # Users for WIT5 dependencies Schemas
  schema {
    name                     = "apiuser"
    attribute_data_type      = "Boolean"
    mutable                  = true
    required                 = false
    developer_only_attribute = false
  }

  schema {
    name                     = "wit_zabbix"
    attribute_data_type      = "Boolean"
    mutable                  = true
    required                 = false
    developer_only_attribute = false
  }

  schema {
    name                     = "user_powerbi"
    attribute_data_type      = "String"
    mutable                  = true
    required                 = false
    developer_only_attribute = false
  }
}

# Users for WIT5 dependencies
resource "aws_cognito_user" "apiuser" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  username     = "apiuser"

  attributes = {
    email          = "apiuser@hashicorp.com" # Alterar para o e-mail WIT 
    email_verified = true
  }
}

resource "aws_cognito_user" "wit_zabbix" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  username     = "wit_zabbix"

  attributes = {
    email          = "wit_zabbix@hashicorp.com" # Alterar para o e-mail WIT
    email_verified = true
  }
}

resource "aws_cognito_user" "user_powerbi" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  username     = "user.powerbi"

  attributes = {
    email          = "user.powerbi@hashicorp.com" # Alterar para o e-mail WIT
    email_verified = true
  }
}

# Groups for WIT5 dependencies
resource "aws_cognito_user_group" "wit_portal_admins" {
  name         = "wit_portal_admins"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Grupo para os usuários que precisam de permissão de operação do monitoramento e do analytics e de permissão para alterar os usuários e grupos."
}

resource "aws_cognito_user_group" "wit_portal_monitoring" {
  name         = "wit_portal_monitoring"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Grupo para os usuários que precisam de permissão de acesso ás funcionalidades de monitoramento"
}

# Add apiuser and user_powerbi in wit_portal_admins
resource "aws_cognito_user_in_group" "add_apiuser_in_wit_portal_admins" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  group_name   = aws_cognito_user_group.wit_portal_admins.name
  username     = aws_cognito_user.apiuser.username
}

resource "aws_cognito_user_in_group" "add_user_powerbi_in_wit_portal_admins" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  group_name   = aws_cognito_user_group.wit_portal_admins.name
  username     = aws_cognito_user.user_powerbi.username
}

# Add apiuser, user_powerbi and wit_zabbix in wit_portal_monitoring
resource "aws_cognito_user_in_group" "add_wit_zabbix_in_wit_portal_monitoring" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  group_name   = aws_cognito_user_group.wit_portal_monitoring.name
  username     = aws_cognito_user.wit_zabbix.username
}

resource "aws_cognito_user_in_group" "add_apiuser_in_wit_portal_monitoring" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  group_name   = aws_cognito_user_group.wit_portal_monitoring.name
  username     = aws_cognito_user.apiuser.username
}

resource "aws_cognito_user_in_group" "add_user_powerbi_in_wit_portal_monitoring" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  group_name   = aws_cognito_user_group.wit_portal_monitoring.name
  username     = aws_cognito_user.user_powerbi.username
}

# Client
resource "aws_cognito_user_pool_client" "client" {
  name = "WIT 5 - Terraform Dev" # Nome do Cliente

  user_pool_id                  = aws_cognito_user_pool.user_pool.id
  generate_secret               = true
  refresh_token_validity        = 30
  prevent_user_existence_errors = "ENABLED"
  callback_urls                 = ["https://gov.api.wit.algar.tech"] # Verificar
  supported_identity_providers  = ["COGNITO"]
  # allowed_oauth_flows = ["client_credentials"]
  # allowed_oauth_scopes = ["email", "phone", "openid"]

  explicit_auth_flows = [
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
}

resource "aws_cognito_user_pool_domain" "cognito-domain" {
  domain       = aws_cognito_user_pool.user_pool.name
  user_pool_id = aws_cognito_user_pool.user_pool.id
}

# Identity Pool
resource "aws_cognito_identity_pool" "main" {
  identity_pool_name               = "identity-pool-terraform-dev-lucas" # Alterar para o nome do cliente que está sendo implantado
  allow_unauthenticated_identities = false
  allow_classic_flow               = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.client.id
    provider_name           = aws_cognito_user_pool.user_pool.endpoint
    server_side_token_check = false
  }

  tags = {
    author      = "lucasdscdje@algartech.com" # Alterar para o nome de quem está  implantando
    customer    = "Terraform Teste "          # Alterar para o nome do cliente que está sendo implantado
    environment = "dev"                       # dev ou prod
    project     = "wit5"
  }
}



data "aws_iam_policy_document" "authenticated" {
  statement {
    effect = "Allow"

    principals {
      type        = "Federated"
      identifiers = ["cognito-identity.amazonaws.com"]
    }

    actions = ["sts:AssumeRoleWithWebIdentity"]

    condition {
      test     = "StringEquals"
      variable = "cognito-identity.amazonaws.com:aud"
      values   = [aws_cognito_identity_pool.main.id]
    }

    condition {
      test     = "ForAnyValue:StringLike"
      variable = "cognito-identity.amazonaws.com:amr"
      values   = ["authenticated"]
    }
  }
}

resource "aws_iam_role" "authenticated" {
  name               = "cognito_authenticated"
  assume_role_policy = data.aws_iam_policy_document.authenticated.json
}

data "aws_iam_policy_document" "authenticated_role_policy" {
  statement {
    effect = "Allow"

    actions = [
      "mobileanalytics:PutEvents",
      "cognito-sync:*",
      "cognito-identity:*",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "authenticated" {
  name   = "authenticated_policy"
  role   = aws_iam_role.authenticated.id
  policy = data.aws_iam_policy_document.authenticated_role_policy.json
}

resource "aws_cognito_identity_pool_roles_attachment" "main" {
  identity_pool_id = aws_cognito_identity_pool.main.id

  # role_mapping {
  #   identity_provider         = "graph.facebook.com"
  #   ambiguous_role_resolution = "AuthenticatedRole"
  #   type                      = "Rules"

  #   mapping_rule {
  #     claim      = "isAdmin"
  #     match_type = "Equals"
  #     role_arn   = aws_iam_role.authenticated.arn
  #     value      = "paid"
  #   }
  # }

  roles = {
    "authenticated" = aws_iam_role.authenticated.arn
  }

}