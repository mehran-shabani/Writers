# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

ARG USERNAME=vscode

# Install system dependencies, docker CLI + compose plugin, Python toolchain, and utilities
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        python3-pip \
        python3-dev \
        build-essential \
        make \
        git \
        curl \
        ca-certificates \
        docker.io \
        docker-compose-plugin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ensure the docker group exists and add the non-root user to it for Docker access
RUN groupadd --force docker \
    && usermod -aG docker ${USERNAME}

# Default to bash shell
SHELL ["/bin/bash", "-c"]

