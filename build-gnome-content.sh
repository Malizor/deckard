#!/usr/bin/env bash

# Deckard, a Web based Glade Runner
# Copyright (C) 2013-2019  Nicolas Delvaux <contact@nicolas-delvaux.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


command -v xmllint >/dev/null 2>&1 || { echo >&2 "This script requires the xmllint command. Aborting."; exit 1; }
command -v git >/dev/null 2>&1 || { echo >&2 "This script requires the git command. Aborting."; exit 1; }
command -v rsync >/dev/null 2>&1 || { echo >&2 "This script requires the rsync command. Aborting."; exit 1; }
command -v curl >/dev/null 2>&1 || { echo >&2 "This script requires the curl command. Aborting."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo >&2 "This script requires the jq command. Aborting."; exit 1; }
command -v broadwayd >/dev/null 2>&1 || { echo >&2 "This script requires the broadwayd command. Aborting."; exit 1; }

# The following is necessary for X-less servers
export GDK_BACKEND=broadway
broadwayd :99 & # Ensure we do not conflict with the Deckard instance
bPID=$! # broadwayd is killed at the end of the script
trap "kill -9 $bPID; exit" SIGHUP SIGINT SIGTERM # ensure it is killed even if the script is aborted
export BROADWAY_DISPLAY=:99


# Supported locales
locales=(af_ZA \
         am_ET \
         an_ES \
         ar_AE \
         as_IN \
         ast_ES \
         az_AZ \
         be_BY \
         bem_ZM \
         bn_IN \
         brx_IN \
         bs_BA \
         ca_ES \
         cs_CZ \
	 cy_GB \
         da_DK \
         de_DE \
         el_GR \
         en_AU \
         eo \
         es_ES \
         et_EE \
         eu_ES \
         fi_FI \
         fur_IT \
         fr_FR \
         gd_GB \
         gl_ES \
         gu_IN \
         he_IL \
         hi_IN \
         hr_HR \
         hu_HU \
         hy_AM \
         id_ID \
         is_IS \
         it_IT \
         ja_JP \
         kn_IN \
         ko_KR \
         lt_LT \
         lv_LV \
         mai_IN \
         mg_MG \
         mk_MK \
         ml_IN \
         mn_MN \
         mr_IN \
         ms_MY \
         my_MM \
         nb_NO \
         nds_NL \
         ne_NP \
         nl_NL \
         nn_NO \
         nso_ZA \
         oc_FR \
         or_IN \
         pa_IN \
         pl_PL \
         pt_BR \
         pt_PT \
         ro_RO \
         ru_RU \
         rw_RW \
         si_LK \
         sk_SK \
         sl_SI \
         sq_AL \
         sr_RS \
         sv_SE \
         ta_IN \
         te_IN \
         tg_TJ \
         th_TH \
         tr_TR \
         ug_CN \
         uk_UA \
         uz_UZ \
         vi_VN \
         wa_BE \
         xh_ZA \
         zh_CN \
         zh_HK \
         zh_TW \
         zu_ZA)


# Project blacklist
# List of modules known to contain nothing displayable by Deckard
# This list avoid us to clone these projects for nothing.
modules_blacklist=(adwaita-icon-theme \
                   amtk \
                   at-spi2-core \
                   atk \
                   atomato \
                   cantarell-fonts \
                   caribou \
                   chrome-gnome-shell \
                   clutter \
                   clutter-gtk \
                   cogl \
                   damned-lies \
                   dconf \
                   desktop-icons \
                   ekiga \
                   evolution-activesync \
                   evolution-ews \
                   evolution-mapi \
                   extensions-web \
                   flatpak \
                   folks \
                   gcab \
                   gdk-pixbuf \
                   gdl \
                   gdm \
                   gegl \
                   genius \
                   ghex \
                   gimp-gap \
                   gimp-help \
                   gimp-tiny-fu \
                   glib \
                   glib-networking \
                   glib-openssl \
                   gnome-backgrounds \
                   gnome-commander \
                   gnome-directory-thumbnailer \
                   gnome-dvb-daemon \
                   gnome-font-viewer \
                   gnome-getting-started-docs \
                   gnome-hello \
                   gnome-internet-radio-locator \
                   gnome-keyring \
                   gnome-latex \
                   gnome-menus \
                   gnome-notes \
                   gnome-online-accounts \
                   gnome-settings-daemon \
                   gnome-shell \
                   gnome-shell-extensions \
                   gnome-sound-recorder \
                   gnome-themes-extra \
                   gnome-tweaks \
                   gnome-user-docs \
                   gnome-user-share \
                   gnome-video-effects \
                   gnomemm-website \
                   goocanvas \
                   gparted \
                   grilo \
                   grilo-plugins \
                   gsettings-desktop-schemas \
                   gtk \
                   gtk-doc \
                   gtk-mac-integration \
                   gtk-vnc \
                   gucharmap \
                   gvfs \
                   gxml \
                   jhbuild \
                   json-glib \
                   lasem \
                   libgdata \
                   libgnome-games-support \
                   libgovirt \
                   libgsf \
                   libgtop \
                   libgweather \
                   libpeas \
                   library-web \
                   libsecret \
                   libsoup \
                   libwnck \
                   ModemManager \
                   msitools \
                   mutter \
                   nautilus-sendto \
                   NetworkManager \
                   notification-daemon \
                   pan \
                   phodav \
                   polkit \
                   PulseAudio \
                   quadrapassel \
                   release-notes \
                   sushi \
                   template-glib \
                   tepl \
                   totem-pl-parser \
                   tracker-miner-chatlog \
                   tracker-miners \
                   video-subtitles \
                   vino \
                   webkit \
                   xdg-desktop-portal \
                   xdg-user-dirs-gtk \
                   yelp \
                   yelp-xsl)

isBlacklisted () {
    for item in "${modules_blacklist[@]}"; do
        [[ "$item" == "$1" ]] && return 0
    done
    return 1
}


# Get a single module
function get_module {
    module_name=$1
    module_url=$2
    mkdir -p $module_name

    # Repositories are cached locally
    if [ -d "../cache/$module_name/.git" ]; then
	echo "Updating the cached $module_name repository..."
	cd ../cache/$module_name
	git fetch origin
	git reset --hard origin/master
	git gc --prune=now  # Minimize disk space
	cd -
    else
	echo "Getting $module_name (as it was not found in the cache)..."
	mkdir -p ../cache
	cd ../cache
	git clone $module_url
	cd -
	echo "$module_name was downloaded and cached."
    fi

    # Copy the module to a work directory
    rm -rf workdir
    rsync -rq --exclude=.git ../cache/$module_name/ workdir

    # Build locals
    for lang in ${locales[@]}; do
        # Try to figure out the PO name from the locale name
        IFS="_."
        unset lstring
        for i in $lang; do lstring+=($i); done
        unset IFS

        if [ -f workdir/po/$lang.po ]; then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module_name.mo workdir/po/$lang.po
        elif [ -f workdir/po/${lstring[0]}_${lstring[1]}.po ]; then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module_name.mo workdir/po/${lstring[0]}_${lstring[1]}.po
        elif [ -f workdir/po/${lstring[0]}.po ]; then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module_name.mo workdir/po/${lstring[0]}.po
        else
            echo "No PO file found for $lang in $module_name!"
        fi
    done

    # Detect and keep relevant folders
    folders=(`find workdir -iregex ".*\.\(ui\|xml\|glade\)" -printf '%h\n' | sort -u`)
    for folder in ${folders[@]}; do
	cp --parents -r $folder $module_name
    done
    # Move all the tree up
    mv $module_name/workdir/* $module_name
    rm -rf $module_name/workdir
    # We don't need the clone anymore
    rm -rf workdir

    # Remove unwanted files
    find $module_name -not -iregex ".*\.\(ui\|xml\|glade\|png\|jpg\|jpeg\|svg\)" | xargs rm 2> /dev/null

    # Basic check to remove non-glade files
    find $module_name -iregex ".*\.\(ui\|xml\|glade\)" -exec sh -c 'xmllint --xpath /interface {} 2> /dev/null > /dev/null || (echo {} is not valid, removing it... && rm -f {})' \;

    # We don't support odd glade files with type-func attributes (evolution, I'm looking at you)
    rm -f $(grep -lr "type-func" .)

    # Some glade files do not contain anything displayable (eg: cheese, data/cheese-actions.ui)
    cd ..
    find content_tmp/$module_name -iregex ".*\.\(ui\|xml\|glade\)" -exec python3 -c "
import os, sys
from gladerunner import GladeRunner
gr = GladeRunner('{}')
try:
    gr.load()
except Exception as exp:
    print('{} is not loadable (%s), removing it...' % exp)
    os.remove('{}')
    sys.exit()
if len(gr.windows) == 0:
    print('Nothing is displayable in {}, removing it...')
    os.remove('{}')
" \; 2> /dev/null

    cd content_tmp

    # Remove empty folders
    find $module_name -type d -empty -exec rmdir -p 2> /dev/null {} \;

    # Is there anything left?
    if [[ -z $(find $module_name -iregex ".*\.\(ui\|xml\|glade\)") ]]; then
	echo "Nothing is displayable in the $module_name module!"
	rm -rf $module_name
    fi
}


# The script starts here
rm -rf content_tmp

for lang in "${locales[@]}"; do
    mkdir -p "content_tmp/LANGS/$lang/LC_MESSAGES"
done

cd content_tmp


# Get all translatable projects from Damned-Lies
modules=$(curl --silent https://l10n.gnome.org/api/v1/modules/ | jq -r .[].href)
for module in $modules; do
    module=$(curl --silent https://l10n.gnome.org$module)
    name=$(echo $module | jq -j .name)
    web_url=$(echo $module | jq -j .vcs_web)
    ext_platform=$(echo $module | jq -j .ext_platform)
    clone_url=${web_url%/}.git
    # We only want projects translated on Damned-Lies.
    # Others most likely have no use of Deckard anyway.
    if [[ $ext_platform ]]; then
        continue
    fi
    if isBlacklisted $name; then
       echo "Ignoring $name, as it is blacklisted."
       continue
    fi

    # Actually retrieve the module
    get_module $name $clone_url
done


# Remember when this was done
date -Is > timestamp

kill -9 $bPID

# We are done, now replace the old content folder (if any)
cd ..
rm -rf content
mv content_tmp content
