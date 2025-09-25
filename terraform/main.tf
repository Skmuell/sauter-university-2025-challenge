terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.13.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  billing_project = var.gcp_project_id
  user_project_override = true
}

resource "google_project_service" "apis" {
  project = var.gcp_project_id
  for_each = toset([
    "serviceusage.googleapis.com",
    "cloudresourcemanager.googleapis.com", 
    "iam.googleapis.com", 
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "iamcredentials.googleapis.com",
    "monitoring.googleapis.com",
    "billingbudgets.googleapis.com",
    "cloudbilling.googleapis.com", 
    "aiplatform.googleapis.com"
  ])
  service                    = each.key
  disable_on_destroy         = false
  disable_dependent_services = true
}

// Creating Resources
resource "google_storage_bucket" "ons_data" {
  name          = "${var.gcp_project_id}-ons-raw-data"
  location      = var.gcp_region
  force_destroy = true 
  depends_on = [google_project_service.apis]
}

# BigQuery Dataset
resource "google_bigquery_dataset" "dataset_ons" {
  dataset_id = "hydrological_data_ons"
  project    = var.gcp_project_id
  location   = var.gcp_region
  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "dataset_trusted" {
  dataset_id = "trusted_data" 
  project    = var.gcp_project_id
  location   = var.gcp_region
  depends_on = [google_project_service.apis]
}

resource "google_artifact_registry_repository" "artifact_registry_repository" {
  location      = var.gcp_region
  repository_id = "agents-api-repo" # Repository Name
  description   = "Repository for agent API images."
  format        = "DOCKER"
  depends_on = [google_project_service.apis]
}

resource "google_cloud_run_v2_service" "api_agents" {
  name     = "api-agents"
  location = var.gcp_region
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"

      env {
        name  = "PROJECT_ID"
        value = var.gcp_project_id
      }
      env {
        name  = "GCS_BUCKET_NAME"
        value = google_storage_bucket.ons_data.name
      }
      env {
        name  = "BQ_DATASET" 
        value = google_bigquery_dataset.dataset_ons.dataset_id
      }
      env {
        name  = "BQ_TABLE"
        value = "trusted_ear_diario_por_reservatorio"
      }
      env {
        name  = "DATASET_TRUSTED"
        value = google_bigquery_dataset.dataset_trusted.dataset_id
      }
      env {
        name  = "DATASET_RAW"
        value = google_bigquery_dataset.dataset_ons.dataset_id
      }
    }
    
  }

}

# Billing Limit and Budget alerts
resource "google_billing_budget" "budget" {
  billing_account = var.billing_account_id
  display_name    = "Project Budget"

  budget_filter {
    projects = ["projects/${var.gcp_project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "BRL"
      units         = "300"
    }
  }

  # Rule to send alerts to defined emails
  all_updates_rule {
    monitoring_notification_channels = [
      google_monitoring_notification_channel.email_channel.id,
    ]
  }

  threshold_rules {
    threshold_percent = 0.2
  }
  threshold_rules {
    threshold_percent = 0.5
  }
  threshold_rules {
    threshold_percent = 0.8
  }
}

resource "google_monitoring_notification_channel" "email_channel" {
  display_name = "Email Channel for Budget Alerts"
  type         = "email"
  labels = {
    email_address = var.notification_emails[0]
  }
}