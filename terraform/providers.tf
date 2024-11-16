terraform {
  required_version = ">= 0.14"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.26"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12.1"
    }
  }

  backend "local" {
    path = "state/terraform.tfstate"
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/local_config"
  config_context = var.k8s_context
}

provider "helm" {
  kubernetes {
    config_path    = "~/.kube/local_config"
    config_context = var.k8s_context
  }
}
