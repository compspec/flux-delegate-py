FROM fluxrm/flux-sched:jammy

LABEL maintainer="Vanessasaurus <@vsoch>"

# Match the default user id for a single system so we aren't root
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
ENV USERNAME=${USERNAME}
ENV USER_UID=${USER_UID}
ENV USER_GID=${USER_GID}
USER root

# extra interactive utilities
RUN apt-get update \
 && apt-get -qq install -y --no-install-recommends \
    fd-find \
    less \
    bats \
    ripgrep \
    lsb-release \
    gnupg2

# Python depedencies
RUN python3 -m pip install fractale && \
    wget https://downloads.skewed.de/skewed-keyring/skewed-keyring_1.3_all_$(lsb_release -s -c).deb && \
    dpkg -i skewed-keyring_1.3_all_$(lsb_release -s -c).deb

# Add the group and user that match our ids
RUN groupadd -g ${USER_GID} ${USERNAME} && \
    adduser --disabled-password --uid ${USER_UID} --gid ${USER_GID} --gecos "" ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers
USER $USERNAME
