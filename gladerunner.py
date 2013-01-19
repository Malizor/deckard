#!/usr/bin/env python3

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

"""Module to load a Glade file and display its windows"""

from gi.repository import Gtk, GObject

import os
import sys
import fcntl
import locale
import argparse
from threading import Timer

placeholder_widget = """
class %(name)s(Gtk.Label):
    __gtype_name__ = '%(name)s'

    def __init__(self):
        Gtk.Label.__init__(self, "<span foreground='#DD4814'>"
                                     "<i>unknown widget</i></span>")
        self.set_use_markup(True)
"""


class GladeRunner:
    """Module to load a Glade file and display all windows in it"""

    def __init__(self, glade_file_path, gettext_domain=None,
                 lang_path='None', language='POSIX', suicidal=False):
        """Create the GladeRunner instance"""
        self.glade_file_path = glade_file_path
        self.lang_path = lang_path
        self.gettext_domain = gettext_domain
        self.builder = Gtk.Builder()
        self.windows = {}

        if suicidal:
            # Set STDIN to be non-blocking
            fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
            fcntl.fcntl(sys.stdin, fcntl.F_SETFL, fl | os.O_NONBLOCK)
            t = Timer(5, self.nde)
            t.daemon = True
            t.start()

        if 'LANGUAGE' in os.environ:
            # Useful when running from command-line
            del os.environ['LANGUAGE']
        locale.setlocale(locale.LC_ALL, language)

    def nde(self):
        """Near Death Experience

        Try to read from stdin. If there is nothing, commit suicide.
        """
        message = sys.stdin.readlines()
        if len(message) > 0:
            # Someone loves me!
            t = Timer(5, self.nde)
            t.daemon = True
            t.start()
        else:
            # I'm forever alone, this life is not worth living...
            Gtk.main_quit()
            os._exit(0)

    def load(self):
        """Load the provided glade file"""
        locale.bindtextdomain(self.gettext_domain, self.lang_path)
        locale.textdomain(self.gettext_domain)

        self._load()

        for obj in self.builder.get_objects():
            # disable FileChooser (it can be a security issue)
            if isinstance(obj, Gtk.FileChooser):
                obj.set_sensitive(False)
                continue
            # remove links
            if hasattr(obj, 'do_activate_link'):
                obj.connect('activate-link', self.ignore_link)
            if hasattr(obj, 'is_toplevel') and obj.is_toplevel():
                name = Gtk.Buildable.get_name(obj)
                if name is None:
                    name = 'gladerunner%d' % len(self.windows)
                self.windows[name] = obj

        if len(self.windows) == 0:
            # Try to get higher level widgets and put them in windows
            toplevel = set()
            for obj in self.builder.get_objects():
                if hasattr(obj, 'get_toplevel'):
                    toplevel.add(obj.get_toplevel())
            for obj in toplevel:
                if hasattr(obj, 'is_toplevel') and obj.is_toplevel():
                    # This is most likely a menu. It is probably embeded
                    # in another window, so we can ignore it
                    continue
                window = Gtk.Window()
                name = Gtk.Buildable.get_name(obj)
                if name is None:
                    name = 'gladerunner%d' % len(self.windows)
                Gtk.Buildable.set_name(window, name)
                window.set_title(name)
                window.add(obj)
                self.windows[name] = window

    def _load(self):
        """Try to load a glade file.

        If an unknown widget is found, try to use a placeholder instead.
        """
        try:
            self.builder.add_from_file(self.glade_file_path)
        except Exception as e:
            # Try to detect if we miss a custom widget
            message = str(e)
            if message.startswith("Invalid object type `"):
                try:
                    # This will fails if this placeholder was already defined
                    exec(placeholder_widget % {'name': message[21:-1]})
                    self._load()
                except:
                    print(message)
                    sys.exit(1)
            else:
                print(message)
                sys.exit(1)

    def display(self):
        """Display all windows"""
        if len(self.windows) == 0:
            print('Nothing to display. Did you load the file first?')
            sys.exit(1)
        else:
            for name in self.windows:
                self.windows[name].connect("delete-event", self.close_window)
                self.windows[name].show_all()
            GObject.threads_init()
            Gtk.main()

    @classmethod
    def ignore_link(cls, _):
        """Do not try to open links"""
        return True

    def close_window(self, window, _):
        """Close this window and quit if no more windows are displayed"""
        window.destroy()
        del self.windows[Gtk.Buildable.get_name(window)]
        if len(self.windows) == 0:
            Gtk.main_quit()


def parse():
    """Argument parsing"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--suicidal', action='store_true')
    parser.add_argument('glade_file_path')
    parser.add_argument('gettext_domain', default='None', nargs='?')
    parser.add_argument('language', default='POSIX', nargs='?')
    parser.add_argument('lang_path', default=None, nargs='?')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse()
    gr = GladeRunner(args.glade_file_path,
                     args.gettext_domain,
                     args.lang_path,
                     args.language,
                     args.suicidal)
    gr.load()
    gr.display()
