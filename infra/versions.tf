terraform {
  required_version = ">= 1.10"

  required_providers {
    docker = {
      # BLANK 1 - who publishes the Docker provider? namespace/name, as on the registry
      source = "kreuzwerker/docker"
      # BLANK 2 - a constraint that accepts new 4.x releases and never 5.0
      version = "~> 4.6"
    }
  }
}
