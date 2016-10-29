# This Dockerfile is experimental: it is not production ready.
# However, it may also be seen as a step-by-step tutorial for a manual installation.

FROM ubuntu:16.10
MAINTAINER Nicolas Delvaux, contact@nicolas-delvaux.org


RUN apt-get update
RUN apt-get upgrade -y


# Install dependencies
RUN apt-get install -y nginx  gir1.2-gtk-3.0 python3-gi python3-jinja2
RUN apt-get install --no-install-recommends -y sudo uwsgi uwsgi-plugin-python3 git ca-certificates gettext libxml2-utils rsync gnome-themes-standard language-pack-gnome-*

# Install some fonts to cover most languages
RUN apt-get install -y ttf-ubuntu-font-family fonts-lohit-guru fonts-guru-extra fonts-guru fonts-droid-fallback fonts-dejavu-extra fonts-khmeros-core fonts-lklug-sinhala fonts-sil-padauk fonts-nanum

# Make sure that all locales are generated
RUN dpkg-reconfigure locales -fnoninteractive


# Create a dedicated user
RUN useradd deckard --create-home -s /usr/sbin/nologin -g www-data

# Configure GTK decorations
RUN sudo -u deckard mkdir -p ~deckard/.config/gtk-3.0
RUN echo -e "[Settings]\ngtk-theme-name = Adwaita\ngtk-fallback-icon-theme = gnome\n" | sudo -u deckard tee ~deckard/.config/gtk-3.0/settings.ini > /dev/null


# Now install deckard itself!

# Get the source code
RUN cd ~deckard && sudo -u deckard git clone http://github.com/Malizor/deckard.git ~deckard/deckard-app

# Setup uWSGI
RUN cp ~deckard/deckard-app/INSTALL/nginx+uwsgi/uwsgi/deckard.ini /etc/uwsgi/apps-available/deckard.ini
RUN ln -s /etc/uwsgi/apps-available/deckard.ini /etc/uwsgi/apps-enabled/deckard.ini

# Setup nginx
RUN cp ~deckard/deckard-app/INSTALL/nginx+uwsgi/nginx/deckard.conf /etc/nginx/sites-available/deckard.conf
RUN ln -s /etc/nginx/sites-available/deckard.conf /etc/nginx/sites-enabled/deckard.conf
RUN rm /etc/nginx/sites-enabled/default
#RUN systemctl restart nginx


# Deckard itself is installed now, we only miss data from gnome.org
RUN cd ~deckard && export PYTHONPATH=~deckard/deckard-app && sudo -u deckard ~deckard/deckard-app/build-gnome-content.sh

# Auto-update the content folder once a day
RUN echo "0 2 * * * PYTHONPATH=~deckard/deckard-app ~deckard/deckard-app/build-gnome-content.sh" | sudo -u deckard crontab -

# Configure Deckard to use our content folder
RUN echo -e "[deckard]\ncontent_dir_path = /home/deckard/content" | sudo -u deckard tee ~deckard/deckard.conf > /dev/null

# Point uWSGI to our configuration file
RUN echo "env = DECKARD_CONF_FILE=/home/deckard/deckard.conf" >> /etc/uwsgi/apps-enabled/deckard.ini
#RUN systemctl restart uwsgi


# Expose nginx
EXPOSE 80

# Create the startup script
# The trailing "cat" is actually a hack to keep the container alive...
RUN echo -e "#!/usr/bin/env sh\nservice nginx start; service uwsgi start; cat" > start_script.sh

CMD start_script.sh
