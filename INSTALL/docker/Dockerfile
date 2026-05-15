FROM ubuntu:26.04

LABEL org.opencontainers.image.authors="Nicolas Delvaux <contact@nicolas-delvaux.org>"

ARG DEBIAN_FRONTEND=noninteractive
ARG AUTO_RELOAD_ON_CODE_CHANGE=false

ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ------------------------------------------------------------
# Base system packages
# ------------------------------------------------------------

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        supervisor \
        nginx \
        uwsgi \
        uwsgi-plugin-python3 \
        ca-certificates \
        gettext \
        libxml2-utils \
        jq \
        rsync \
        curl \
        language-pack-gnome-* \
   && apt-get install -y \
        gir1.2-gtk-3.0 \
        gir1.2-handy-1 \
        python3-gi \
        python3-jinja2 \
        python3-multipart \
        fonts-ubuntu \
        fonts-lohit-guru \
        fonts-guru-extra \
        fonts-guru \
        fonts-dejavu-extra \
        fonts-droid-fallback \
        fonts-khmeros-core \
        fonts-lklug-sinhala \
        fonts-sil-padauk \
        fonts-nanum \
        fonts-telu \
        fonts-samyak \
        fonts-knda \
        fonts-beng \
        fonts-sil-abyssinica \
        fonts-thai-tlwg-ttf \
    && dpkg-reconfigure locales \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Dedicated application user
# ------------------------------------------------------------

RUN useradd \
    --create-home \
    --shell /usr/sbin/nologin \
    --gid www-data \
    deckard

# ------------------------------------------------------------
# Retrieve the application
# ------------------------------------------------------------

WORKDIR /home/deckard

COPY ../.. /home/deckard/deckard-app
RUN chown -R deckard:www-data /home/deckard/deckard-app

# ------------------------------------------------------------
# GTK configuration
# ------------------------------------------------------------

RUN mkdir -p /home/deckard/.config/gtk-3.0 && \
    printf '[Settings]\ngtk-theme-name = Adwaita\ngtk-fallback-icon-theme = gnome\n' \
        > /home/deckard/.config/gtk-3.0/settings.ini && \
    chown -R deckard:www-data /home/deckard/.config

# ------------------------------------------------------------
# uWSGI configuration
# ------------------------------------------------------------

RUN cp /home/deckard/deckard-app/INSTALL/nginx+uwsgi/uwsgi/deckard.ini \
        /etc/uwsgi/apps-available/deckard.ini && \
    ln -s /etc/uwsgi/apps-available/deckard.ini \
        /etc/uwsgi/apps-enabled/deckard.ini && \
    mkdir -p /run/uwsgi/app/deckard && \
    chown deckard:www-data /run/uwsgi/app/deckard

# ------------------------------------------------------------
# nginx configuration
# ------------------------------------------------------------

RUN cp /home/deckard/deckard-app/INSTALL/nginx+uwsgi/nginx/deckard.conf \
        /etc/nginx/sites-available/deckard.conf && \
    ln -s /etc/nginx/sites-available/deckard.conf \
        /etc/nginx/sites-enabled/deckard.conf && \
    rm -f /etc/nginx/sites-enabled/default


# ------------------------------------------------------------
# Deckard configuration
# ------------------------------------------------------------

RUN printf '[deckard]\ncontent_dir_path = /home/deckard/data/content\n' \
        > /home/deckard/deckard.conf && \
    chown deckard:www-data /home/deckard/deckard.conf && \
    /bin/echo "env = DECKARD_CONF_FILE=/home/deckard/deckard.conf" >> /etc/uwsgi/apps-enabled/deckard.ini


RUN if [ "$AUTO_RELOAD_ON_CODE_CHANGE" = "true" ]; then \
        echo 'py-autoreload = 1' >> /etc/uwsgi/apps-enabled/deckard.ini ; \
    else \
        echo 'py-autoreload = 0' >> /etc/uwsgi/apps-enabled/deckard.ini ; \
    fi

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/home/deckard/deckard-app/INSTALL/docker/resources/supervisor.conf"]
