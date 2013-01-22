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

"""Sessions handling and utilities for the deckard project"""

import os
import shutil
import tempfile
from uuid import uuid4
from threading import Lock, Timer
from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError

locale_language_mapping = {
    'POSIX': 'No translation',
    'ar_AE.UTF-8': 'العربية',
    'ca_ES.UTF-8': 'Català',
    'cs_CZ.UTF-8': 'Čeština',
    'da_DK.UTF-8': 'Dansk',
    'de_DE.UTF-8': 'Deutsch',
    'el_GR.UTF-8': 'ελληνικά',
    'en_US.UTF-8': 'English (US)',
    'es_ES.UTF-8': 'Español',
    'et_EE.UTF-8': 'Eesti keel',
    'fi_FI.UTF-8': 'Suomi',
    'fr_FR.UTF-8': 'Français',
    'gl_ES.UTF-8': 'Galego',
    'hr_HR.UTF-8': 'Hrvatski jezik',
    'hu_HU.UTF-8': 'Magyar',
    'nb_NO.UTF-8': 'Bokmål',
    'nl_NL.UTF-8': 'Nederlands',
    'he_IL.UTF-8': 'עִבְרִית',
    'is_IS.UTF-8': 'Íslenska',
    'it_IT.UTF-8': 'Italiano',
    'ja_JP.UTF-8': '日本語',
    'ko_KR.UTF-8': '한국말',
    'lt_LT.UTF-8': 'Lietuvių kalba',
    'nn_NO.UTF-8': 'Nynorsk',
    'pl_PL.UTF-8': 'Język polski',
    'pt_BR.UTF-8': 'Português (Brasil)',
    'pt_PT.UTF-8': 'Português',
    'ro_RO.UTF-8': 'Română',
    'ru_RU.UTF-8': 'Pусский язык',
    'sk_SK.UTF-8': 'Slovenčina',
    'sl_SI.UTF-8': 'Slovenščina',
    'sv_SE.UTF-8': 'Svenska',
    'th_TH.UTF-8': 'ภาษาไทย',
    'tr_TR.UTF-8': 'Türkçe',
    'ug_CN.UTF-8': 'ئۇيغۇرچە',
    'zh_CN.UTF-8': '汉语'
}


class DeckardException(Exception):
    """Standard exception"""
    def __init__(self, short, log):
        Exception.__init__(self, '%s\n\n%s' % (short, log))


class Session:
    """
    This represents a Deckard session for one user.
    It manages its gladerunner instance (both launch and keep-alive) and custom
    PO files.
    Everything is cleaned-up when the session is deleted.
    """

    def __init__(self, uuid, gladerunner, content_root):
        self.port = 0
        self.uuid = uuid  # unique id to avoid session spoofing
        self.process = None
        self.custom_po = OrderedDict()  # {po_name: (module, root_path)}
        self.removable = False  # can the manager delete this Session?
        self.gladerunner = gladerunner
        self.content_root = content_root
        self.max_custom_po = 4

    def spawn_runner(self, module, module_file, language, port):
        """Launch a gladerunner instance.

        If a running process is attached to this session, it will be replaced.
        """
        self.port = port
        env = {
            'GDK_BACKEND': 'broadway',
            'UBUNTU_MENUPROXY': '',
            'LIBOVERLAY_SCROLLBAR': '0',
            'BROADWAY_DISPLAY': str(port)
            }

        if self.process is not None and self.process.poll() is None:
            self.process.kill()

        if language in self.custom_po:
            if self.custom_po[language][0] != module:
                raise DeckardException('"%s" does not exist' % language,
                                       'No such file was registered for the '
                                       '%s module.' % module)
            lang_root = os.path.join(self.custom_po[language][1], 'LANGS')
            # This locale has to be available on your system
            language = 'en_US.UTF-8'
        else:
            lang_root = os.path.join(self.content_root, 'LANGS')

        self.process = Popen([self.gladerunner,
                              '--suicidal',
                              os.path.join(self.content_root,
                                           module,
                                           module_file),
                              module,
                              language,
                              lang_root],
                             stdin=PIPE,
                             env=env)

    def store_po(self, fd, name, module):
        """Store a custom PO file.

        If a file with the same name is attached to this session, it will be
        replaced.
        Returns a dictionary, associating all relevant modules with a list of
        stored PO files for it on this session, from the older to the newest.
        """
        lang_root = tempfile.mkdtemp(prefix='deckard_')
        po_path = os.path.join(lang_root, 'file.po')
        po = open(po_path, 'bw')
        for line in fd:
            po.write(line)
        po.close()

        # create necessary directories
        mo_path = os.path.join(lang_root, 'LANGS', 'en', 'LC_MESSAGES')
        os.makedirs(mo_path)

        try:
            check_output(['msgfmt',
                          '--check',
                          '--use-fuzzy',
                          '--output-file',
                          os.path.join(mo_path, module) + '.mo',
                          po_path],
                         stderr=STDOUT)
        except CalledProcessError as e:
            shutil.rmtree(lang_root)
            # We don't need to expose the file name
            log = e.output.decode('unicode_escape').replace('%s:' % po_path, '')
            raise DeckardException('Error while building the .mo', log)

        if name in self.custom_po:
            shutil.rmtree(self.custom_po[name][1])
            del self.custom_po[name]  # drop to re-add at the end of the queue
        elif len(self.custom_po) >= self.max_custom_po:
            # delete the oldest
            shutil.rmtree(self.custom_po.popitem(last=False)[1][1])

        self.custom_po[name] = (module, lang_root)

        res = {}
        for item in self.custom_po:
            if self.custom_po[item][0] not in res:
                res[self.custom_po[item][0]] = [item]
            else:
                res[self.custom_po[item][0]].append(item)
        return res

    def keep_process_alive(self):
        """Beg the runner (if any) to stay alive

        Returns True if the message was sent, False if it wasn't (eg. if there
        is no process)."""
        if self.process is not None and self.process.poll() is None:
            self.process.stdin.write(b'Please stay alive!')
            return True
        return False

    def is_removable(self):
        """State if this Session is removable.

        Returns True if no running process is attached to this Session and
        if no PO file is stored.
        It also returns True if this Session was tagged as removable.
        Otherwise, this function will return False."""
        if self.removable:
            return True
        elif self.process is None or self.process.poll() is not None:
            if len(self.custom_po) == 0:
                return True
        return False

    def __del__(self):
        """Kill the process if it is running and delete any custom PO files"""
        if self.process is not None and self.process.poll() is None:
            self.process.kill()
        for name in self.custom_po:
            shutil.rmtree(self.custom_po[name][1])


class SessionsManager:
    """Helper to manage all Deckard sessions."""

    def __init__(self, gladerunner, content_root):
        self.content_root = content_root
        self.gladerunner = gladerunner
        self.first_port = 2019
        self.max_users = 10
        self.sessions = {}  # Sessions, by UUID
        self._lock = Lock()  # allows to only manipulate one session at a time

        self._cleanup_loop_running = False

    def _get_session(self, uuid):
        """Returns the Session object from an UUID.

        Returns None if the Session does not exist."""
        if uuid in self.sessions:
            return self.sessions[uuid]
        else:
            return None

    def _create_session(self):
        """Create a new session an returns its uuid

        Raise an exception if we don't have room for one more session.
        """
        if len(self.sessions) >= self.max_users:
            raise DeckardException('Too many users!',
                                   'For performance purposes, this '
                                   'application is currently limited to %d '
                                   'simultaneous sessions.\n'
                                   'You may want to retry in a few minutes.'
                                   % self.max_users)
        uuid = str(uuid4())
        self.sessions[uuid] = Session(uuid,
                                      self.gladerunner,
                                      self.content_root)
        if not self._cleanup_loop_running:
            self._cleanup_loop(init=True)  # Restart the cleanup loop
            self._cleanup_loop_running = True
        return uuid

    def _find_free_port(self):
        """Returns a free port ready to be used by a session.

        Checked ports are between first_port and (first_port + max_users - 1).
        """
        for port in range(self.first_port,
                          self.first_port + self.max_users):
            next = False
            for uuid in self.sessions:
                if self.sessions[uuid].port == port:
                    next = True
                    break
            if not next:
                return port

        # No free port!
        # This should never if you managed to create a session
        raise DeckardException('Could not find a free port.',
                               'This should never happen.\n'
                               'Please report this bug.')

    def spawn_runner(self, uuid, module, module_file, language):
        """Ask a session to launch a gladerunner instance.

        If a running process is attached to this session, it will be replaced.
        Returns a tuple with the session uuid and the port of the launched
        instance.
        """
        with self._lock:
            # get or create the session
            session = self._get_session(uuid)
            if session is None:
                uuid = self._create_session()
                session = self._get_session(uuid)
            else:
                session._removable = False

            if session.port == 0:
                port = self._find_free_port()
            else:
                port = session.port  # Reuse the same port

            session.spawn_runner(module, module_file, language, port)

            return uuid, port

    def store_po(self, uuid, fd, name, module):
        """Ask a session to store a PO file.

        If a file with the same name is attached to this session, it will be
        replaced.
        Returns a tuple with the session uuid and a dictionary, associating all
        relevant modules with a list of stored PO files for it on this session,
        from the older to the newest.
        """
        with self._lock:
            # get or create the session
            session = self._get_session(uuid)
            if session is None:
                uuid = self._create_session()
                session = self._get_session(uuid)
            else:
                session.removable = False
                session.keep_process_alive()  # if any
            return uuid, session.store_po(fd, name, module)

    def keep_alive(self, uuid):
        """Keep the uuid session alive a bit more.

        Returns False in case of problem (the session is already dead?),
        True otherwise."""
        with self._lock:
            session = self._get_session(uuid)
            if session is not None:
                session.removable = False
                session.keep_process_alive()  # if any
                return True
            return False

    def _cleanup_loop(self, timer=5, init=False):
        """Delete garbage sessions regularly.

        If init is True, do not acquire lock in this iteration."""
        if not init:
            self._lock.acquire()
        try:
            for uuid in list(self.sessions.keys()):
                if not init and self.sessions[uuid].is_removable():
                    del self.sessions[uuid]
                else:
                    # This session may be deleted next time (if no keep_alive)
                    self.sessions[uuid].removable = True

            if len(self.sessions) > 0:
                Timer(timer, self._cleanup_loop, (timer,)).start()
            else:
                # Break the loop when there is no more sessions
                self._cleanup_loop_running = False
        finally:
            if not init:
                self._lock.release()
