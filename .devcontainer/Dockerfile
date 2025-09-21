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
ENV PIXI_HOME=/opt/pixi
ENV PATH=/opt/pixi/bin:$PATH
COPY pixi.toml pixi.lock /opt/pixi/
WORKDIR /opt/pixi
RUN /bin/bash -c "curl -fsSL https://pixi.sh/install.sh | bash"  && pixi install

# Need to "install" fluxion
RUN git clone --depth 1 https://github.com/flux-framework/flux-sched /tmp/flux-sched
ENV PYTHONPATH=/usr/lib/python3.10/site-packages:/tmp/flux-sched/src/python

# This should be set in the pixi environment
ENV NO_AT_BRIDGE=1

# Add the group and user that match our ids
RUN groupadd -g ${USER_GID} ${USERNAME} && \
    adduser --disabled-password --uid ${USER_UID} --gid ${USER_GID} --gecos "" ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers
USER $USERNAME
