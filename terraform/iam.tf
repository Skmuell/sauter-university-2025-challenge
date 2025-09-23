

resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-agentes-sa"
  display_name = "Service Account for Cloud Run Agents API"
}

resource "google_project_iam_member" "bigquery_user_cloud_run" {
  project = var.gcp_project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_service" "vertex_ai_api" {
  project            = var.gcp_project_id
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

resource "google_cloud_run_v2_service_iam_member" "allow_public_invocation" {
  project  = google_cloud_run_v2_service.api_agents.project
  location = google_cloud_run_v2_service.api_agents.location
  name     = google_cloud_run_v2_service.api_agents.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# -- PERMISSIONS FOR AUTOMATION (GITHUB ACTIONS) --
resource "google_service_account" "github_actions_sa" {
  account_id   = "github-actions-sa"
  display_name = "Service Account for GitHub Actions CI/CD"
}

# Permissions the pipeline needs to deploy
resource "google_project_iam_member" "github_actions_roles" {
  project = var.gcp_project_id
  for_each = toset([
    "roles/run.admin",             
    "roles/artifactregistry.admin", 
    "roles/iam.serviceAccountUser" 
  ])
  role   = each.key
  member = google_service_account.github_actions_sa.member
}

# Workload Identity for securely connecting to GitHub
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-pool"
  display_name              = "Workload Identity Pool for CI/CD"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "Github Actions Provider"
  attribute_mapping = {
    "google.subject"       = "assertion.sub",
    "attribute.repository" = "assertion.repository",
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Allows the GitHub repository to use the Service Account
resource "google_service_account_iam_member" "github_wif_user" {
  service_account_id = google_service_account.github_actions_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_repo}"
}