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
var stored_po = {};
var upload_button = document.getElementById('upload_button');
var upload_spinner = document.getElementById('upload_spinner');
var po_picker = document.getElementById('po_file')
var module_selector = document.getElementById('module_selector');
var current_ui_selector = document.getElementById('ui_selector_' + module_selector.value);

var locale_selector = document.getElementById('language_selector');
var language_count = locale_selector.length;

switch_ui_selector(); // initialize the file selector

var iframe = document.getElementById('iframe');
iframe.src = 'about:blank';

// URL parameters handling
var param_locale = getParameterByName('locale');
if (!param_locale) {
    // No locale was specified, try to preselect the browser language
    param_locale = window.navigator.userLanguage || window.navigator.language;
    // Browsers use RFC 4646 to represent locales
    param_locale = param_locale.replace('-', '_');
    if (param_locale == 'en') { // Special case
        param_locale = 'POSIX';
    }
}

for (var i = 0; i < locale_selector.length; i++) {
    if (locale_selector[i].label.indexOf(param_locale) == 0) {
        locale_selector.selectedIndex = i;
        break;
    }
}

var param_module = getParameterByName('module');
var valid_param_module = false;
if (param_module) {
    // select this module (if it exists)
    for (var i = 0; i < module_selector.length; i++) {
        if (module_selector[i].label == param_module) {
            valid_param_module = true;
            module_selector.selectedIndex = i;
            switch_ui_selector();
            break;
        }
    }
}

var param_ui = getParameterByName('ui');
if (param_ui) {
    // select this ui (if it exists)
    for (var i = 0; i < current_ui_selector.length; i++) {
        if (current_ui_selector[i].label == param_ui) {
            current_ui_selector.selectedIndex = i;
            break;
        }
    }
}

var param_display = getParameterByName('display');

var param_file = getParameterByName('file');
if (param_file) {
    // A valid module must has been selected at the same time
    if (!valid_param_module) {
        alert('You must specify a valid module via the "module" parameter.');
    } else {
        // Ask the server to get this file from l10n.gnome.org
        upload_po(param_file);
    }
} else if (param_display == '1') {
    // The 'display' parameter should only affect the initial loading
    param_display = '0';
    // Display the preselected view
    spawn();
}


function getParameterByName(name) {
    name = name.replace(/[\[]/, '\\\[').replace(/[\]]/, '\\\]');
    var regex_string = '[\\?&]' + name + '=([^&#]*)';
    var regex = new RegExp(regex_string);
    var results = regex.exec(window.location.search);
    if(!results) {
        return null;
    } else {
        return decodeURIComponent(results[1].replace(/\+/g, ' '));
    }
}

function get_url_for_this_view() {
    var url = 'http://'+document.domain+'/?module='+module_selector.value+'&ui='+current_ui_selector.value;
    var i = locale_selector.value.indexOf('\u2003');
    if (i == -1) {
        if (locale_selector.value == param_file) {
            url += '&file='+locale_selector.value;  // PO from l10n.gnome.org
        } // else, this is a PO uploaded from the user. It is useless for other users.
    } else {
        url += '&locale='+locale_selector.value.substr(0, i);
    }
    document.getElementById('url_view').innerHTML = url;
}

function switch_ui_selector() {
    current_ui_selector.style.display = 'none';
    current_ui_selector = document.getElementById('ui_selector_' + module_selector.value);
    current_ui_selector.style.display = 'block';
    refresh_lang_list();  // if there is any custom PO for this module
}

function refresh_lang_list() {
    // rebuild the language list
    locale_selector.length = language_count;
    if (stored_po[module_selector.value]) {
        for (var i = 0; i < stored_po[module_selector.value].length; i++) {
            var option = document.createElement('option');
            option.text = stored_po[module_selector.value][i];
            locale_selector.add(option);
        }
    }
}

function check_file() {
    str = po_picker.value.toUpperCase();
    if (str == '') {
    return -1
    }
    suffix = '.PO';
    if(str.indexOf(suffix, str.length - suffix.length) == -1) {
        alert('File type not allowed.\nExpected a *.po file.');
        po_picker.value = '';
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

function upload_po(file_name_on_l10ngnome) {
    var data = new FormData();
    if (file_name_on_l10ngnome) {
        data.append('po_name', file_name_on_l10ngnome);
    } else {
        data.append('po_name', po_picker.value);
        data.append('po_file', po_picker.files[0]);
    }
    data.append('po_module', module_selector.value);

    if (session != '') {
        // Attach to the current session
        data.append('session', session);
        clearInterval(keep_alive_loop);
    }

    upload_spinner.style.display = 'block';
    upload_button.disabled = true;
    po_picker.disabled = true;
    current_ui_selector.disabled = true;
    module_selector.disabled = true;
    locale_selector.disabled = true;
    xml_http_post('#', data, upload_po_return);
}

function upload_po_return(req) {

    upload_spinner.style.display = 'none';
    upload_button.disabled = false;
    po_picker.disabled = false;
    current_ui_selector.disabled = false;
    module_selector.disabled = false;
    locale_selector.disabled = false;

    if (req.status == 413 || req.status == 0) {
        alert('This file exceed the maximum size.');
        abort_session();
        return;
    }

    res = JSON.parse(req.responseText);
    if (res['status'] == 'ok') {
        session = res['session'];
        stored_po = res['custom_files'];
        refresh_lang_list();
        if (stored_po[module_selector.value]) {
            locale_selector.selectedIndex = locale_selector.length - 1;  // focus the last item
        }

        keep_alive_loop = setInterval(keep_alive, 2000);
        if (param_display == '1') {
            // The 'display' parameter should only affect the initial loading
            param_display = '0';
            // Display the preselected view
            spawn();
        }
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
    var data = 'action=spawn&module='+module_selector.value+'&file='+current_ui_selector.value;
    var i = locale_selector.value.indexOf('\u2003');
    if (i == -1) {
        data += '&lang='+locale_selector.value;  // custom PO
    } else {
        data += '&lang='+locale_selector.value.substr(0, i);
    }
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
            // change the '/' before the port by a ':' if you did not configure a proxy to redirect runner ports on port 80
            iframe.src = 'http://'+document.domain+'/'+res['port']+'/';
        }
        // Wait for the remote process to be fully started
        iframe.src = 'ressources/waiting.html';
        if (process_running) {
            setTimeout(update_iframe, 700);
        } else {
            // Wait a bit more if we don't replace a running process
            setTimeout(update_iframe, 1700);
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
    locale_selector.length = language_count;
    document.getElementById('user_count').innerHTML = 'disconnected';
    stored_po = {};
}
