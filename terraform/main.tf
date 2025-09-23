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
}

// API´s 
resource "google_project_service" "storage_api" {
  service = "storage.googleapis.com"
}

resource "google_project_service" "bigquery_api" {
  service = "bigquery.googleapis.com"
}

resource "google_project_service" "artifactregistry_api" {
  service = "artifactregistry.googleapis.com"
}

resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
}

// Creating Resources
resource "google_storage_bucket" "ons_data" {
  name          = "${var.gcp_project_id}-ons-raw-data"
  location      = var.gcp_region
  force_destroy = true 
}

# BigQuery Dataset
resource "google_bigquery_dataset" "dataset_ons" {
  dataset_id = "hydrological_data_ons"
  project    = var.gcp_project_id
  location   = var.gcp_region
}

resource "google_artifact_registry_repository" "artifact_registry_repository" {
  location      = var.gcp_region
  repository_id = "agents-api-repo" # Repository Name
  description   = "Repository for agent API images."
  format        = "DOCKER"
}

resource "google_project_iam_member" "bigquery_viewer_cloud_run" {
  project = var.gcp_project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_cloud_run_v2_service" "api_agents" {
  name     = "api-agents"
  location = var.gcp_region
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
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