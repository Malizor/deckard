Deckard installation How-To
===========================

In the following procedure we will assume you use at least Ubuntu 16.04.
Other distributions should work fine too, but Deckard was mainly developped
and tested on Ubuntu.

The recommended setup for Deckard is throught uWSGI and Nginx.  
Other setups should work to, but are not tested.
Example configuration files for Apache (libapache2-mod-wsgi-py3) and HAProxy are
provided for information in the `INSTALL/apache+haproxy` folder.

Dependencies
------------

You will need the following packages on Ubuntu/Debian:


* gir1.2-gtk-3.0
* python3
* python3-gi
* python3-jinja2
* uwsgi and uwsgi-plugin-python3
* nginx

You will want to use the latest version of GTK+ if your interfaces depend on
newly introduced widgets. For doing so, you should have to use the latest
release of your distribution.  
For example, on https://deckard.malizor.org, Deckard is hosted in a LXD container
with the latest Ubuntu version, the host being an Ubuntu LTS.


Installation
------------

Deckard will be ran as a dedicated user to secure things a bit.

- Create a user named `deckard` and its home directory  
`sudo useradd deckard --create-home -s /usr/sbin/nologin -g www-data`

- Copy the source folder content in `/home/deckard/deckard-app`  
  Of course, all files should belong to the `deckard` user.

- Copy `INSTALL/nginx+uwsgi/uwsgi/deckard.ini` to `/etc/uwsgi/apps-available/deckard.ini`  
  You may want to edit this file, mainly to make it point to your own `deckard.conf` file.

- Enable the Deckard application in uWSGI  
`ln -s /etc/uwsgi/apps-available/deckard.ini /etc/uwsgi/apps-enabled/deckard.ini`

- Copy `INSTALL/nginx+uwsgi/nginx/deckard.conf` to `/etc/nginx/sites-available/deckard.conf`

- Enable the Deckard site in Nginx  
`ln -s /etc/nginx/sites-available/deckard.conf /etc/nginx/sites-enabled/deckard.conf`

Now that Deckard itself is installed, you will have to generate the content that will be displayed!
(please see the `Content` part below)



Content
-------

The Deckard app will look for a `content` folder in it's root.
It must have a specific layout. Here is a sample tree of it:

```
content/
├── module1
│   └── ....
├── module2
│   └── ....
└── LANGS
    ├── fr_FR
    │   └── LC_MESSAGES
    │       ├── module1.mo
    │       └── module2.mo
    └── es_ES
        └── LC_MESSAGES
            ├── module1.mo
            └── module2.mo
```

The `LANGS` tree should not surprise you if you are familiar with Gettext.
The organization of files in modules folders is up to you.

`build-gnome-content.sh` is the script that is used on https://deckard.malizor.org to
automatically generate the content folder from Gnome git. A Cron job is used to
run it once a day, in order to remain up-to-date.  
You may want to reuse or to adapt this script for your particular project.


FAQ
---

### My windows are ugly!


You may want to install this package:
`gnome-themes-standard`

If still no theme is applied to your windows, you can edit
`~/.config/gtk-3.0/settings.ini`
and add the following lines:

```ini
[Settings]
gtk-theme-name = Adwaita
gtk-fallback-icon-theme = gnome
```

### Some locales do not work!

Please run:
`locale -a`

If your locale is not in the list, then you need to enable it.  
On Ubuntu systems, you need to add your locale in
`/var/lib/locales/supported.d/local`
Then you have to run:  
`sudo dpkg-reconfigure locales`

A simpler way, if you use Ubuntu, is to run this command:  
`sudo apt install language-pack-gnome-* --no-install-recommends`

### UI are not reversed in RTL locales!

You have to install Gtk translations for the specified locale.
For example, for Arabian on Ubuntu:  
`sudo apt install language-pack-gnome-ar-base --no-install-recommends`

### Chars are not displayed properly!

On Ubuntu, installing the following packages should cover most fonts you may need:  
`sudo apt install ttf-ubuntu-font-family fonts-lohit-guru fonts-guru-extra fonts-guru fonts-droid-fallback fonts-dejavu-extra fonts-khmeros-core fonts-lklug-sinhala fonts-sil-padauk fonts-nanum fonts-telu fonts-samyak fonts-knda fonts-beng fonts-sil-abyssinica fonts-thai-tlwg-ttf`
