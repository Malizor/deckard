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

# Supported locales
locales=(ar_AE.UTF-8 \
         bn_IN.UTF-8 \
         ca_ES.UTF-8 \
         cs_CZ.UTF-8 \
         da_DK.UTF-8 \
         de_DE.UTF-8 \
         el_GR.UTF-8 \
         es_ES.UTF-8 \
         et_EE.UTF-8 \
         fi_FI.UTF-8 \
         fr_FR.UTF-8 \
         gl_ES.UTF-8 \
         he_IL.UTF-8 \
         hi_IN.UTF-8 \
         hr_HR.UTF-8 \
         hu_HU.UTF-8 \
         id_ID.UTF-8 \
         is_IS.UTF-8 \
         it_IT.UTF-8 \
         ja_JP.UTF-8 \
         ko_KR.UTF-8 \
         lt_LT.UTF-8 \
         nb_NO.UTF-8 \
         nn_NO.UTF-8 \
         nl_NL.UTF-8 \
         pa_IN.UTF-8 \
         pl_PL.UTF-8 \
         pt_BR.UTF-8 \
         pt_PT.UTF-8 \
         ro_RO.UTF-8 \
         ru_RU.UTF-8 \
         sk_SK.UTF-8 \
         sl_SI.UTF-8 \
         sv_SE.UTF-8 \
         tg_TJ.UTF-8 \
         th_TH.UTF-8 \
         tr_TR.UTF-8 \
         ug_CN.UTF-8 \
         zh_CN.UTF-8)

rm -rf content_tmp

for lang in "${locales[@]}"
do
    mkdir -p "content_tmp/LANGS/$lang/LC_MESSAGES"
done

function get_module {
    module=$1
    echo "Getting $module..."
    mkdir -p $module
    git clone --depth 1 git://git.gnome.org/$module tmp_clone

    # Build locals
    for lang in ${locales[@]}
    do
        # Try to figure out the PO name from the locale name
        IFS="_."
        unset lstring
        for i in $lang; do lstring+=($i); done
        unset IFS

        if [ -f tmp_clone/po/$lang.po ]
        then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module.mo tmp_clone/po/$lang.po
        elif [ -f tmp_clone/po/${lstring[0]}_${lstring[1]}.po ]
        then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module.mo tmp_clone/po/${lstring[0]}_${lstring[1]}.po
        elif [ -f tmp_clone/po/${lstring[0]}.po ]
        then
            msgfmt --output-file LANGS/$lang/LC_MESSAGES/$module.mo tmp_clone/po/${lstring[0]}.po
        else
            echo "No PO file found for $lang in $module!"
        fi
    done

    # Detect and keep relevant folders
    folders=(`find tmp_clone -name *.ui -printf '%h\n' | sort -u`)
    for folder in ${folders[@]}
    do
	cp --parents -r $folder $module
    done
    # Move all the tree up
    mv $module/tmp_clone/* $module
    rm -rf $module/tmp_clone
    # We don't need the clone anymore
    rm -rf tmp_clone

    # Remove unwanted files
    find $module -not -name *.ui -a -not -name *.png -a -not -name *.jpg -a -not -name *.jpeg -a -not -name *.svg  | xargs rm 2> /dev/null

    # Basic check to remove non-glade files
    find $module -name *.ui -exec sh -c 'xmllint --xpath /interface/object {} 2> /dev/null > /dev/null || (echo {} is not valid, removing it... && rm -f {})' \;

    # We don't support odd glade files with type-func attributes (evolution, I'm looking at you)
    rm -f $(grep -lr "type-func" .)

    # Some glade files do not contain anything displayable (eg: cheese, data/cheese-actions.ui)
    cd ..
    find content_tmp/$module -name *.ui -exec python3 -c "
import os
from gladerunner import GladeRunner
gr = GladeRunner('{}')
gr.load()
if len(gr.windows) == 0:
    print('Nothing is displayable in {}, removing it...')
    os.remove('{}')
" \; 2> /dev/null
    cd content_tmp

    # Remove empty folders
    find $module -type d -empty -exec rmdir 2> /dev/null {} \;
}

cd content_tmp

# Get relevant modules
get_module alacarte
get_module anjuta
get_module anjuta-extras
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
get_module gcalctool
get_module gedit
get_module gedit-latex
get_module gedit-plugins
get_module gnome-bluetooth
get_module gnome-chess
get_module gnome-color-manager
get_module gnome-control-center
get_module gnome-dictionary
get_module gnome-disk-utility
get_module gnome-nettool
get_module gnome-session
get_module gnome-sudoku
get_module gnome-system-log
get_module gnome-system-monitor
get_module gnome-terminal
get_module gnumeric
get_module goffice
get_module gpointing-device-settings
get_module gthumb
get_module gtranslator
get_module iagno
get_module libgnome-media-profiles
get_module meld
get_module monkey-bubble
get_module mousetweaks 
get_module nanny
get_module nemiver
get_module network-manager-applet
get_module network-manager-openvpn
get_module network-manager-pptp
get_module orca
get_module pitivi
get_module rhythmbox
get_module rygel
get_module sabayon
get_module sound-juicer
get_module swell-foop
get_module totem
get_module tracker
get_module transmageddon
get_module vinagre
get_module vino
get_module zenity

# We are done, now replace the old content folder (if any)
cd ..
rm -rf content
mv content_tmp content
