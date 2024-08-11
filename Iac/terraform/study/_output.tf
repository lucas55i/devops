output "client_id" {
    value = nonsensitive(aws_cognito_user_pool_client.client.id)
}

output "client_secret" {
    value = nonsensitive(aws_cognito_user_pool_client.client.client_secret)
}