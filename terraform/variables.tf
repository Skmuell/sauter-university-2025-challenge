
variable "gcp_project_id" {
  type    = string
  default = "projeto-teste-473013" 
}

variable "gcp_region" {
  type    = string
  default = "us-central1"
}

variable "billing_account_id" {
  type        = string
  description = "Billing Account ID" # Exemple: 010101-F0FFF0-10XX01
}

variable "github_repo" {
  type        = string
  description = "The name of the repository on GitHub in the format 'user/repo-name'."
}

variable "notification_emails" {
  type        = list(string)
  description = "Email list to receive quote alerts."
}