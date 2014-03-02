#!/usr/bin/env python3

# Deckard, a Web based Glade Runner
# Copyright (C) 2013-2014 Nicolas Delvaux <contact@nicolas-delvaux.org>

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

import os
import sys
import fcntl
import locale
import signal
import ctypes
import builtins
import argparse
import importlib
from threading import Timer
from subprocess import Popen
import xml.etree.ElementTree as ET

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

    def __init__(self, glade_file_path, gettext_domain='foobar',
                 lang_path=None, language='POSIX', suicidal=False):
        """Create the GladeRunner instance"""

        # Late import because of potential environment tweaking outside of
        # the class (start_broadwayd)
        builtins.Gtk = importlib.import_module('gi.repository.Gtk')
        builtins.GObject = importlib.import_module('gi.repository.GObject')

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
        """Process and load the provided glade file

        The file content is processed by:
         - taking care of templates
         - deleting unknown internal children
         - replacing unknown widgets by placeholders
         - disabling "dangerous" widgets like file choosers
         - giving a window to window-less highest level widgets
        """

        # Parse the Glade file as XML for additional processing
        tree = ET.parse(self.glade_file_path)

        # Substitute templates (if any) for actual objects
        # We can't reliably figure out how these templates are mapped by their
        # true consumers, so we use the 'parent' attribute to substitute them.
        # This attribute is an annotation used by the Glade program for the
        # same purpose, so this is not as hackish as it seems.
        for template in tree.findall('.//template'):
            if 'parent' not in template.keys():
                # We can't substitute this template (no annotation)
                continue
            template.tag = 'object'
            template.set('id', template.get('class'))
            template.set('class', template.get('parent'))
            del template.attrib['parent']

        # The locale has to be set before GTK loads the file
        locale.bindtextdomain(self.gettext_domain, self.lang_path)
        locale.textdomain(self.gettext_domain)

        self._load(tree)

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
            # Try to get highest level widgets and put them in windows
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

    def _load(self, tree):
        """Try to load a Glade file from an ElementTree.

        If an unknown widget is found, try to use a placeholder instead.
        """
        try:
            self.builder.add_from_string(ET.tostring(tree.getroot()).decode())
        except Exception as e:
            message = str(e)
            # Try to detect if we miss a custom widget
            if message.startswith('Invalid object type `'):
                try:
                    # This will fail if this placeholder was already defined
                    exec(placeholder_widget % {'name': message[21:-1]})
                    self._load(tree)
                except:
                    sys.exit(message)
            # Any unknown internal child?
            elif message.startswith('Unknown internal child: '):
                # Just try to delete it.
                # Not sure if this is the best thing to do, but it allows the
                # display of some more UI (like in Epiphany)
                deleted = False
                for obj in tree.findall('.//object'):
                    # we can't "findall child" directly because we need
                    # to remove from the parent
                    for child in obj.findall('child'):
                        if child.get('internal-child') == message[24:]:
                            deleted = True
                            obj.remove(child)
                if deleted:
                    self._load(tree)
                else:
                    # No infinite loop please
                    sys.exit(message)
            else:
                sys.exit(message)

    def display(self):
        """Display all windows"""
        if len(self.windows) == 0:
            sys.exit('Nothing to display. Did you load the file first?')
        else:
            for name in self.windows:
                self.windows[name].connect('delete-event', self.close_window)
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


def start_broadwayd(port):
    """Start a broadwayd daemon on the specified port"""
    display = ':%d' % port
    libc = ctypes.CDLL('libc.so.6')
    # Send a SIGTERM to the child when its parent die
    set_pdeathsig = lambda: libc.prctl(1, signal.SIGTERM)
    Popen(['broadwayd', '--port', str(port), display],
          preexec_fn=set_pdeathsig)
    os.putenv('BROADWAY_DISPLAY', display)


def parse():
    """Argument parsing"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--suicidal', action='store_true',
                        help="Try to read from STDIN each 5 seconds. "
                        "If there is nothing to read, exit.")
    parser.add_argument('-b', '--with-broadwayd', type=int,
                        help="Start a broadwayd daemon on the specified port "
                        "and display through it. "
                        "This option is required for GTK+ >= 3.8.")
    parser.add_argument('glade_file_path')
    parser.add_argument('gettext_domain', default='foobar', nargs='?')
    parser.add_argument('language', default='POSIX', nargs='?')
    parser.add_argument('lang_path', default=None, nargs='?')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse()
    if args.with_broadwayd is not None:
        start_broadwayd(args.with_broadwayd)

    gr = GladeRunner(args.glade_file_path,
                     args.gettext_domain,
                     args.lang_path,
                     args.language,
                     args.suicidal)
    gr.load()
    gr.display()
