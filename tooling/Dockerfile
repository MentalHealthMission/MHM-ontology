# Multi-arch base; fine on Apple Silicon (arm64) and x86_64
FROM eclipse-temurin:17-jre

ARG ROBOT_VERSION=1.9.6
ARG JENA_VERSION=4.10.0

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    PATH=/opt/robot/bin:/opt/apache-jena-$JENA_VERSION/bin:$PATH \
    ROBOT_JAVA_ARGS="-Xmx4G"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl unzip ca-certificates bash coreutils graphviz \
    && rm -rf /var/lib/apt/lists/*

# Install ROBOT
RUN mkdir -p /opt/robot/bin \
    && curl -fsSL -o /opt/robot/bin/robot.jar \
       https://github.com/ontodev/robot/releases/download/v${ROBOT_VERSION}/robot.jar \
    && printf '#!/usr/bin/env bash\nexec java ${ROBOT_JAVA_ARGS:-} -jar /opt/robot/bin/robot.jar "$@"\n' > /opt/robot/bin/robot \
    && chmod +x /opt/robot/bin/robot

# Install Apache Jena (for riot)
RUN (curl -fsSL -o /tmp/jena.tgz \
      https://downloads.apache.org/jena/binaries/apache-jena-${JENA_VERSION}.tar.gz \
      || curl -fsSL -o /tmp/jena.tgz \
      https://archive.apache.org/dist/jena/binaries/apache-jena-${JENA_VERSION}.tar.gz) \
    && tar -C /opt -xzf /tmp/jena.tgz \
    && rm /tmp/jena.tgz

## Openllet installation intentionally omitted by default.
## If needed later, we can add a conditional build-arg to include it.

WORKDIR /work

# Default command prints versions of installed tools
CMD ["bash","-lc","echo \"ROBOT:\" $(robot --version) && echo \"Jena riot:\" $(riot --version 2>&1 | head -n1)"]
