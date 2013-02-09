<!DOCTYPE html>

<html lang="en">
  <head>
    <title>Deckard: a Web based Glade Runner</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link href="/ressources/deckard.css" rel="stylesheet" type="text/css" media="all" />
  </head>
  <body>
    <h1>Deckard: a Web based Glade Runner</h1>

    <p id="user_count"></p>

    <form id="glade_selector">
      <table>
        <tr>
          <td>Select a module:</td>
          <td>
            <select id="module_selector"  onchange="switch_ui_selector();">
              {% for item in content['MODULES']|dictsort(true) %}
              <option>{{ item[0] }}</option>
              {% endfor %}
            </select>
          </td>
        </tr>
        <tr>
          <td>Select a UI:</td>
          <td>
            {% for item in content['MODULES']|dictsort(true) %}
            <select style="display:none;" id="ui_selector_{{ item[0] }}">
              {% for ui in item[1]|sort(case_sensitive=true) %}
              <option>{{ ui }}</option>
              {% endfor %}
            </select>
            {% endfor %}
          </td>
        </tr>
        <tr>
          <td>Select a language:</td>
          <td>
            <select id="language_selector">
              <option selected="selected">POSIX&emsp;-&emsp;No translation</option>
              {% for lang in content['LANGS']|sort(case_sensitive=true) %}
              <option>{{ lang }}&emsp;-&emsp;{{ content['LANGS'][lang] }}</option>
              {% endfor %}
            </select>
          </td>
        </tr>
      </table>

      <input type="button" value="Display" onclick="spawn();" />
      <br/>
    </form>

    <form id="po_uploader">
      <table>
        <tr>
          <td>Custom PO file for this UI:</td>
          <td><input type="file" id="po_file" onchange="check_file();"></td>
        </tr>
      </table>
      <table>
        <tr>
          <td><input id="upload_button" type="button" value="Upload" onclick="upload_po();" disabled="disabled"></td>
          <td><img id="upload_spinner" src="ressources/spinner_tiny.gif" alt="Uploading..." title="Uploading..."/></td>
        </tr>
      </table>
    </form>

    <iframe id="iframe" src="about:blank"></iframe>
    <p id="get_code"><a title="Launchpad project" href="https://launchpad.net/deckard">Get the code!</a></p>
    <script type="text/javascript" src="ressources/deckard.js"></script>
  </body>
</html>
