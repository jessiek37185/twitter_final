FROM postgres:15

# Install build tools and compile RUM extension from source
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-server-dev-15 \
    git \
    ca-certificates \
    systemtap-sdt-dev \
    && git clone https://github.com/postgrespro/rum.git /tmp/rum \
    && cd /tmp/rum \
    && USE_PGXS=1 make \
    && USE_PGXS=1 make install \
    && rm -rf /tmp/rum \
    && apt-get remove -y build-essential postgresql-server-dev-15 git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

