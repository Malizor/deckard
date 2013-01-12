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

import os
import json
from cgi import FieldStorage
from urllib.parse import parse_qsl
from jinja2 import Environment, FileSystemLoader

import libdeckard

jinja_env = None
deckard_root = None
content_root = None
sessions_manager = None
gladerunner = None


def init(environ):
    """Initialise global variables (at startup)"""
    global deckard_root
    deckard_root = environ['DECKARD_ROOT']

    global content_root
    content_root = os.path.join(deckard_root, 'content')

    global gladerunner
    gladerunner = os.path.join(deckard_root, 'gladerunner.py')

    global jinja_env
    jinja_env = Environment(loader=FileSystemLoader(
            os.path.join(deckard_root, 'ressources')))
    global sessions_manager
    sessions_manager = libdeckard.SessionsManager(gladerunner, content_root)
    sessions_manager.max_users = int(environ['DECKARD_MAX_USERS'])


def application(environ, start_response):
    """Main WSGI entry point"""
    if deckard_root is None:
        init(environ)
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            if environ['CONTENT_TYPE'].startswith('multipart/form-data'):
                fs = FieldStorage(fp=environ['wsgi.input'], environ=environ)
                if 'po_file' not in fs or \
                   'po_name' not in fs or \
                   'po_module' not in fs:
                    raise Exception()

                uuid = None
                if 'session' in fs:
                    uuid = fs['session'].value

                uuid, po_list = sessions_manager.store_po(uuid,
                                                          fs['po_file'].file,
                                                          fs['po_name'].value,
                                                          fs['po_module'].value)
                response = {'status': 'ok',
                            'session': uuid,
                            'custom_files': po_list}

            else:
                request_body_size = int(environ['CONTENT_LENGTH'])
                qsl = environ['wsgi.input'].read(
                    request_body_size).decode('utf-8')
                post = dict(parse_qsl(qsl))

                if post['action'] == 'spawn':
                    uuid = None
                    if 'session' in post:
                        uuid = post['session']

                    uuid, port = sessions_manager.spawn_runner(uuid,
                                                               post['module'],
                                                               post['file'],
                                                               post['lang'])
                    response = {'status': 'ok',
                                'session': uuid,
                                'port': port}

                elif post['action'] == 'keep_alive':
                    if sessions_manager.keep_alive(post['session']):
                        response = {'status': 'ok',
                                    'users_count': str(len(sessions_manager.sessions))}
                    else:
                        # The session is already dead :-(
                        response = {'status': 'error',
                                    'message': 'disconnected'}

                else:
                    response = {'status' : 'error', 'message': 'bad query'}

        except libdeckard.DeckardException as e:
            response = {'status': 'error',
                        'message': str(e)}
        except Exception as e:
            response = {'status' : 'error',
                        'message': 'An error occurred: %s' % str(e)}

        status = '200 OK'
        headers = [('Content-type', 'application/json')]
        start_response(status, headers)
        return [json.dumps(response)]

    else:
        try:
            content = get_content()
            template = jinja_env.get_template('deckard.tpl')
            res = template.render(content=content)
        except Exception as e:
            res = 'Something went wrong: %s' % e
        start_response('200 OK', [('Content-Type', 'text/html')])
        return res


def get_content():
    content = {'LANGS': os.listdir(os.path.join(content_root, 'LANGS')),
               'MODULES': {}}
    for directory in os.listdir(content_root):
        if directory != 'LANGS':
            content['MODULES'][directory] = []

    for module in content['MODULES']:
        mod_root = os.path.join(content_root, module)
        for root, dirs, files in os.walk(mod_root):
            for file in files:
                base, ext = os.path.splitext(file)
                if ext == '.ui':
                    rel_path = os.path.join(root, file).split(mod_root)[1]
                    rel_path = rel_path[1:]  # strip the leading '/'
                    content['MODULES'][module].append(rel_path)
    return content
