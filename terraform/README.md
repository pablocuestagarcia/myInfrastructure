
# Instalación de Nginx Ingress Controller en Kubernetes con Terraform

Este documento describe cómo instalar Nginx Ingress Controller en un clúster de Kubernetes utilizando Terraform. La configuración permite que Nginx Ingress Controller lea reglas Ingress de cualquier namespace y establece la comunicación mediante NodePort, ideal para desarrollo local.

## Estructura de Carpetas Recomendada

La estructura de carpetas sugerida para este proyecto es la siguiente:

```
.
├── README.md
├── terraform
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   └── helm
│       └── nginx-ingress
│           ├── values.yaml
│           └── release.tf
├── kubernetes
│   ├── namespaces
│   ├── ingress
│   └── applications
└── scripts
```

## Configuración con Terraform

### Proveedor de Kubernetes y Helm

En `providers.tf`, configure los proveedores para Kubernetes y Helm:

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}
```

### Instalar Nginx Ingress Controller con Helm

Dentro de `terraform/helm/nginx-ingress/release.tf`:

```hcl
resource "helm_release" "nginx_ingress" {
  name       = "nginx-ingress"
  repository = "https://helm.nginx.com/stable"
  chart      = "nginx-ingress"
  version    = "0.9.1"

  set {
    name  = "controller.service.type"
    value = "NodePort"
  }

  set {
    name  = "controller.watchIngressWithoutClass"
    value = "true"
  }
}
```

### Archivo `main.tf`

En el archivo `main.tf`, incluya la configuración básica de Terraform y referencias a los módulos o recursos desplegados:

```hcl
terraform {
  required_version = ">= 0.12"
}

module "nginx_ingress" {
  source = "./helm/nginx-ingress"
}
```

### Aplicación de la Configuración

Para aplicar la configuración, ejecute los comandos de Terraform:

1. Inicializar Terraform: `terraform init`
2. Revisar el plan de ejecución: `terraform plan`
3. Aplicar la configuración: `terraform apply`

## Conclusión

Siguiendo estos pasos y utilizando la estructura de carpetas recomendada, puede instalar Nginx Ingress Controller en su clúster de Kubernetes de manera organizada y alineada con los principios de GitOps.
