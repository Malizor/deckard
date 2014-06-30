# This Dockerfile is experimental: it is not production ready.
# However, it may also be seen as a step-by-step tutorial for a manual installation.

FROM ubuntu:14.04
MAINTAINER Nicolas Delvaux, contact@nicolas-delvaux.org

# Add my PPA for an HTML5 enabled GTK+
RUN echo "deb http://ppa.launchpad.net/malizor/gtk-broadway/ubuntu trusty main" > /etc/apt/sources.list.d/malizor-gtk-broadway-trusty.list
# Add the key
RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com F829E15318015CCF

RUN apt-get update
RUN apt-get upgrade -y


# Install dependencies
RUN apt-get install -y nginx broadwayd gir1.2-gtk-3.0 python3-gi python3-jinja2
RUN apt-get install --no-install-recommends -y uwsgi uwsgi-plugin-python3 git ca-certificates gettext libxml2-utils gnome-themes-standard language-pack-gnome-*

# Create a dedicated user
RUN useradd deckard --create-home -s /usr/sbin/nologin -g www-data

# Configure GTK decorations
RUN sudo -u deckard mkdir -p ~deckard/.config/gtk-3.0
RUN echo -e "[Settings]\ngtk-theme-name = Adwaita\ngtk-fallback-icon-theme = gnome\n" | sudo -u deckard tee ~deckard/.config/gtk-3.0/settings.ini > /dev/null


# Now install deckard itself!

# Get the source code
RUN cd ~deckard && sudo -u deckard git clone http://github.com/Malizor/deckard.git ~deckard/deckard-app

# Setup uWSGI
RUN cp ~deckard/deckard-app/conf/nginx+uwsgi/uwsgi/deckard.ini /etc/uwsgi/apps-available/deckard.ini
RUN ln -s /etc/uwsgi/apps-available/deckard.ini /etc/uwsgi/apps-enabled/deckard.ini
RUN service uwsgi restart

# Setup nginx
RUN cp ~deckard/deckard-app/conf/nginx+uwsgi/nginx/deckard.conf /etc/nginx/sites-available/deckard.conf
RUN ln -s /etc/nginx/sites-available/deckard.conf /etc/nginx/sites-enabled/deckard.conf
RUN rm /etc/nginx/sites-enabled/default
RUN service nginx restart


# Deckard itself is installed now, we only miss data from gnome.org
RUN sudo -u deckard ~deckard/deckard-app/build-gnome-content.sh

# Auto-update the content folder once a day
RUN echo "0 2 * * * ~deckard/deckard-app/build-gnome-content.sh" | sudo -u deckard crontab -


# Expose nginx
EXPOSE 80

# Create the startup script
# The trailing "cat" is actually a hack to keep the container alive...
RUN echo -e "#!/usr/bin/env sh\nservice nginx start; service uwsgi start; cat" > start_script.sh

CMD start_script.sh
