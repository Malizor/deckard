/* Deckard, a Web based Glade Runner
 * Copyright (C) 2013  Nicolas Delvaux <contact@nicolas-delvaux.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.

 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
 
var session = '';
var process_running = false;
var keep_alive_loop;
var stored_po = Array();
var upload_button = document.getElementById('upload_button');
var upload_spinner = document.getElementById('upload_spinner');
var po_selector = document.getElementById('po_file')
var module_selector = document.getElementById('module_selector');
var current_file_selector = document.getElementById('file_selector_' + module_selector.value);
switch_file_selector(); // initialize the file selector

var langs = document.getElementById('language_selector');
var language_count = langs.length;
var iframe = document.getElementById('iframe');
iframe.src = 'about:blank';

function switch_file_selector() {
    current_file_selector.style.display = 'none';
    current_file_selector = document.getElementById('file_selector_' + module_selector.value);
    current_file_selector.style.display = 'block';
}

function check_file() {
    str = po_selector.value.toUpperCase();
    if (str == '') {
    return -1
    }
    suffix = '.PO';
    if(str.indexOf(suffix, str.length - suffix.length) == -1) {
        alert('File type not allowed.\nExpected a *.po file.');
        po_selector.value = '';
    upload_button.disabled = true;
    return -1;
    }
    upload_button.disabled = false;
    return 0;
}

function xml_http_post(url, data, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            callback(xhr);
        }
    }
    xhr.send(data);
}

function upload_po() {
    var data = new FormData();
    data.append('po_name', po_selector.value);
    data.append('po_file', po_selector.files[0]);
    data.append('po_module', module_selector.value);

    if (session != '') {
        // Attach to the current session
        data.append('session', session);
    clearInterval(keep_alive_loop);
    }

    upload_spinner.style.display = 'block';
    upload_button.disabled = true;
    po_selector.disabled = true;
    xml_http_post('#', data, upload_po_return);
}

function upload_po_return(req) {

    upload_spinner.style.display = 'none';
    upload_button.disabled = false;
    po_selector.disabled = false;

    if (req.status == 413 || req.status == 0) {
        alert('This file exceed the maximum size.');
        abort_session();
        return;
    }

    res = JSON.parse(req.responseText);
    if (res['status'] == 'ok') {
        session = res['session'];

        // rebuild the language list
        langs.length = language_count;
        for (var i = 0; i < res['custom_files'].length; i++) {
            var option = document.createElement('option');
        option.text = res['custom_files'][i];
        langs.add(option);
        }
    langs.selectedIndex = langs.length - 1;  // focus the last item

        keep_alive_loop = setInterval(keep_alive, 2000);
        return;

    } else if (res['status'] == 'error') {
        abort_session();
        alert(res['message']);
        return;
    }

    abort_session();
    alert('An error occured:\n\n' + req.responseText);
}

function spawn() {
    var data = 'action=spawn&module='+module_selector.value+'&file='+current_file_selector.value;
    data += '&lang='+langs.value;
    if (session != '') {
        // Attach to the current session
        data += '&session=' + session;
        clearInterval(keep_alive_loop);
    }
    xml_http_post('#', data, spawn_return);
}

function spawn_return(req) {
    res = JSON.parse(req.responseText);
    if (res['status'] == 'ok') {
        session = res['session'];
        keep_alive_loop = setInterval(keep_alive, 2000);
        function update_iframe() {
            iframe.src = 'http://'+document.domain+':'+res['port'];
        }
        // Wait for the remote process to be fully started
        iframe.src = 'ressources/waiting.html';
        if (process_running) {
            setTimeout(update_iframe, 500);
        } else {
            // Wait a bit more if we don't replace a running process
            setTimeout(update_iframe, 1500);
        }
        process_running = true;
        return;
    } else if (res['status'] == 'error') {
        abort_session();
        alert(res['message']);
        return;
    }

    abort_session();
    alert('An error occured:\n\n' + req.responseText);
}

function keep_alive() {
    var data = 'action=keep_alive&session='+session;
    xml_http_post('#', data, keep_alive_return);
}

function keep_alive_return(req) {
    var res = JSON.parse(req.responseText)
 
    if (res['status'] == 'ok') {
        document.getElementById('user_count').innerHTML = 'Users online: '+res['users_count'];
        return;
    } else if (res['status'] == 'error') {
        clearInterval(keep_alive_loop);
        abort_session();
        return;
    }

    alert('An error occured:\n\n' + req.responseText);
}

function abort_session() {
    session = '';
    process_running = false;
    langs.length = language_count;
    document.getElementById('user_count').innerHTML = 'disconnected';
}
