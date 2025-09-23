
output "cloud_run_service_url" {
  description = "Cloud Run public API"
  value       = google_cloud_run_v2_service.api_agents.uri
}

output "github_actions_service_account" {
  description = "The Service Account email for GitHub Actions. Copy this value to the 'GCP_SERVICE_ACCOUNT' Secret on GitHub."
  value       = google_service_account.github_actions_sa.email
}

output "workload_identity_provider" {
  description = "The name of the Identity Provider (WIF). Copy this value to the 'GCP_WORKLOAD_IDENTITY_PROVIDER' Secret on GitHub."
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}

output "artifact_registry_repository_name" {
  description = "The name of the repository in Artifact Registry where Docker images are stored."
  value       = google_artifact_registry_repository.nosso_repositorio.name
}

output "ons_data_bucket_name" {
  description = "The name of the Cloud Storage bucket for the raw ONS data."
  value       = google_storage_bucket.dados_ons.name
}