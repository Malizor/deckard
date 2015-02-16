#!/usr/bin/env bash

# Deckard, a Web based Glade Runner
# Copyright (C) 2013  Nicolas Delvaux <contact@nicolas-delvaux.org>

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

# The following is necessary for X-less servers
export GDK_BACKEND=broadway
broadwayd :99 & # Ensure we do not conflict with the Deckard instance
bPID=$! # broadwayd is killed at the end of the script
trap "kill -9 $bPID; exit" SIGHUP SIGINT SIGTERM # ensure it is killed even if the script is aborted
export BROADWAY_DISPLAY=:99
# The following is only useful on the (default) Ubuntu desktop
export UBUNTU_MENUPROXY=
export LIBOVERLAY_SCROLLBAR=0

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

rm -rf content_tmp

for lang in "${locales[@]}"
do
    mkdir -p "content_tmp/LANGS/$lang/LC_MESSAGES"
done

function get_module {
    module=$1
    mkdir -p $module

    # Repositories are cached locally
    if [ -d "../cache/$module/.git" ]; then
	echo "Updating the cached $module repository..."
	cd ../cache/$module
	git fetch origin
	git reset --hard origin/master
	git gc --prune=now  # Minimize disk space
	cd -
    else
	echo "Getting $module (as it was not found in the cache)..."
	mkdir -p ../cache
	cd ../cache
	git clone git://git.gnome.org/$module
	cd -
	echo "$module was downloaded and cached."
    fi

    # Copy the module to a work directory
    rm -rf workdir
    rsync -rq --exclude=.git ../cache/$module/ workdir

    # Build locals
    for lang in ${locales[@]}
    do
        # Try to figure out the PO name from the locale name
        IFS="_."
        unset lstring
        for i in $lang; do lstring+=($i); done
        unset IFS

        if [ -f workdir/po/$lang.po ]
        then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module.mo workdir/po/$lang.po
        elif [ -f workdir/po/${lstring[0]}_${lstring[1]}.po ]
        then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module.mo workdir/po/${lstring[0]}_${lstring[1]}.po
        elif [ -f workdir/po/${lstring[0]}.po ]
        then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module.mo workdir/po/${lstring[0]}.po
        else
            echo "No PO file found for $lang in $module!"
        fi
    done

    # Detect and keep relevant folders
    folders=(`find workdir -iregex ".*\.\(ui\|xml\|glade\)" -printf '%h\n' | sort -u`)
    for folder in ${folders[@]}
    do
	cp --parents -r $folder $module
    done
    # Move all the tree up
    mv $module/workdir/* $module
    rm -rf $module/workdir
    # We don't need the clone anymore
    rm -rf workdir

    # Remove unwanted files
    find $module -not -iregex ".*\.\(ui\|xml\|glade\|png\|jpg\|jpeg\|svg\)" | xargs rm 2> /dev/null

    # Basic check to remove non-glade files
    find $module -iregex ".*\.\(ui\|xml\|glade\)" -exec sh -c 'xmllint --xpath /interface {} 2> /dev/null > /dev/null || (echo {} is not valid, removing it... && rm -f {})' \;

    # We don't support odd glade files with type-func attributes (evolution, I'm looking at you)
    rm -f $(grep -lr "type-func" .)

    # Some glade files do not contain anything displayable (eg: cheese, data/cheese-actions.ui)
    cd ..
    find content_tmp/$module -iregex ".*\.\(ui\|xml\|glade\)" -exec python3 -c "
import os, sys
from gladerunner import GladeRunner
gr = GladeRunner('{}')
try:
    gr.load()
except:
    print('{} is not loadable, removing it...')
    os.remove('{}')
    sys.exit()
if len(gr.windows) == 0:
    print('Nothing is displayable in {}, removing it...')
    os.remove('{}')
" \; 2> /dev/null

    cd content_tmp

    # Remove empty folders
    find $module -type d -empty -exec rmdir -p 2> /dev/null {} \;

    # Is there anything left?
    if [[ -z $(find $module -iregex ".*\.\(ui\|xml\|glade\)") ]]
    then
	echo "Nothing is displayable in the $module module!"
	rm -rf $module
    fi
}

cd content_tmp

# Get relevant modules
get_module alacarte
get_module anjuta
get_module anjuta-extras
get_module california
get_module cheese
get_module dasher
get_module empathy
get_module eog
get_module eog-plugins
get_module epiphany
get_module evolution
get_module file-roller
get_module five-or-more
get_module f-spot
get_module gbrainy
get_module geary
get_module gedit
get_module gedit-latex
get_module gedit-plugins
get_module gevice
get_module gitg
get_module glade
get_module gnome-applets
get_module gnome-bluetooth
get_module gnome-boxes
get_module gnome-chess
get_module gnome-calculator
get_module gnome-color-manager
get_module gnome-control-center
get_module gnome-dictionary
get_module gnome-disk-utility
get_module gnome-logs
get_module gnome-music
get_module gnome-nettool
get_module gnome-panel
get_module gnome-session
get_module gnome-sudoku
get_module gnome-system-log
get_module gnome-system-monitor
get_module gnome-terminal
get_module gnumeric
get_module goffice
get_module goobox
get_module gpointing-device-settings
get_module gthumb
get_module gtranslator
get_module libgnome-media-profiles
get_module meld
get_module mousetweaks
get_module nautilus
get_module nemiver
get_module network-manager-applet
get_module network-manager-openvpn
get_module network-manager-pptp
get_module office-runner
get_module orca
get_module pitivi
get_module regexxer
get_module rhythmbox
get_module rygel
get_module shotwell
get_module sound-juicer
get_module swell-foop
get_module totem
get_module tracker
get_module transmageddon
get_module vinagre
get_module zenity

kill -9 $bPID

# Remember when this was done
date -Is > timestamp

# We are done, now replace the old content folder (if any)
cd ..
rm -rf content
mv content_tmp content
