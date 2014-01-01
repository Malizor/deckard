# Deckard, a Web based Glade Runner
# Copyright (C) 2013, 2014  Nicolas Delvaux <contact@nicolas-delvaux.org>

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

"""WSGI handler for Deckard"""

import os
import json
import configparser
from cgi import FieldStorage
from urllib.parse import parse_qsl
from jinja2 import Environment, FileSystemLoader

import libdeckard

jinja_env = None
sessions_manager = None
config = None

default_config = {'content_dir_path': '/home/deckard/content',
                  'gladerunner_path': '/home/deckard/gladerunner.py',
                  'template_dir_path': '/home/deckard/ressources'}

def init(environ):
    """Initialise global variables (at startup)"""

    conf_file = environ.get('DECKARD_CONF_FILE', './deckard.conf')
    if not os.path.isfile(conf_file):
        raise Exception('%s not found' % conf_file)
        
    global config
    config = configparser.ConfigParser(interpolation=None,
                                       inline_comment_prefixes=('#', ';'),
                                       defaults=default_config)
    config.read(conf_file)
    config = config['deckard']


    global jinja_env
    jinja_env = Environment(loader=FileSystemLoader(
        config['template_dir_path']))
    global sessions_manager
    sessions_manager = libdeckard.SessionsManager(config['gladerunner_path'],
                                                  config['content_dir_path'])
    sessions_manager.max_users = int(environ['DECKARD_MAX_USERS'])


def application(environ, start_response):
    """Main WSGI entry point"""
    if config is None:
        init(environ)
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            if environ['CONTENT_TYPE'].startswith('multipart/form-data'):
                fs = FieldStorage(fp=environ['wsgi.input'], environ=environ)
                if 'po_name' not in fs or 'po_module' not in fs:
                    raise Exception('Malformed input')

                uuid = None
                if 'session' in fs:
                    uuid = fs['session'].value

                if 'po_file' in fs:
                    uuid, custom_files = sessions_manager.store_po(uuid,
                                                                   fs['po_name'].value,
                                                                   fs['po_module'].value,
                                                                   fs['po_file'].file)
                else:
                    uuid, custom_files = sessions_manager.store_po(uuid,
                                                                   fs['po_name'].value,
                                                                   fs['po_module'].value)

                response = {'status': 'ok',
                            'session': uuid,
                            'custom_files': custom_files}

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
                    response = {'status': 'error', 'message': 'bad query'}

        except libdeckard.DeckardException as e:
            response = {'status': 'error',
                        'message': str(e)}
        except Exception as e:
            response = {'status': 'error',
                        'message': 'An error occurred: %s' % str(e)}

        status = '200 OK'
        headers = [('Content-type', 'application/json')]
        start_response(status, headers)
        return [json.dumps(response)]

    else:
        try:
            content = sessions_manager.get_displayable_content()
            template = jinja_env.get_template('deckard.tpl')
            res = template.render(content=content)
        except Exception as e:
            res = 'Something went wrong: %s' % e
        start_response('200 OK', [('Content-Type',
                                   'text/html; charset=utf-8')])
        return [res.encode('utf-8')]
