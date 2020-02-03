FROM ubuntu:18.04 as base

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

FROM base AS user_setup

# This Dockerfile adds a non-root user with sudo access. Use the "remoteUser"
# property in devcontainer.json to use it. On Linux, the container user's GID/UIDs
# will be updated to match your local UID/GID (when using the dockerFile property).
# See https://aka.ms/vscode-remote/containers/non-root-user for details.
ARG USERNAME=dfi
ARG USER_UID=503
ARG USER_GID=$USER_UID

RUN apt-get update \
    && apt-get -y install --no-install-recommends sudo 2>&1 \
    && groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    # [Optional] Add sudo support for the non-root user
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# this target is if we want to use the system python, and is a "final target"
FROM user_setup AS system_python

# Configure apt and install packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils dialog 2>&1 \
    #
    # Verify git, process tools, lsb-release (common in install instructions for CLIs) installed
    && apt-get -y install --no-install-recommends \
          curl git iproute2 procps lsb-release python3 ca-certificates \
          python3-setuptools python3-dev netbase libpq-dev sudo 2>&1 \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=dialog

USER $USERNAME
