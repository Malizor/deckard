Deckard: a Web based Glade Runner
=================================

Translators should always test their translations in context but that is not
always convenient and even possible.  
Some UI need particular conditions to be displayed. Think of error messages or
dialogs that are only displayed when some specific device is plugged in.

Also, the process of building the development version of a program from
sources just to be able to test new translations is time consuming and may not
be accessible to translators who are not also programmers.

This is where Deckard can help.

### What it is

This Web application allows translators to display Glade interfaces in their Web
browsers. They can chose the language of their views and even upload their own
PO files in order to test their work as they translate.

### Instance example

For Gnome projects:  
[http://deckard.malizor.org](http://deckard.malizor.org)  
(all UI and translations files are updated from master once a day)


### FAQ

#### How can I install it?

Please refer to the **INSTALL** file.

#### Why GTK? Why not $toolkit?

Deckard relies on the HTML5 backend for GTK+, also known as "broadway".  
If $toolkit can also targets HTML5, it may be possible to add support for it
in Deckard. Feel free to report a feature request!

#### Why only Glade interfaces and not plain GTK?

This is the only safe way for an open instance.  
Running a full third party app would allow users to mess around with the server
files and settings. We don't want that.  
Aggressively sand-boxing apps that were not designed for that usually just
prevent them to run. We don't want that either.

This is why Deckard uses its own program to load and run Glade files securely.
(see **gladerunner.py**) 

Also, dealing with Glade files allows to display them directly, even if they
may not be easily accessible in the true application.

#### How does it work?

Here is a quick summary:

  * **gladerunner.py** is the program used to display Glade files with specific
translations. It can be used in a stand alone way and is not restricted to
HTML5 rendering. Try the --help option for usage information.

  * **libdeckard.py** contains all the session logic in Deckard.  
Each user is associated to one Session. A Session can spawn a gladerunner.py
process and store custom PO files.
One of the SessionsManager tasks is to keep the whole thing clean (no process or
file leak).

  * **wsgi/deckard.wsgi** is the main Deckard entry point. All it does is wiring
between Web requests and libdeckard.py.

  * **resources/** contains all the Web files (JavaScript, HTML template, CSS...)

Please refer to individual files for further documentation.

#### Can this be integrated in $translation_platform?

Yes!

The easy approach would be to run your own Deckard instance and to add links
to it in your platform.  
Deckard support a number of URL parameters that allow to pre-select the right
UI file in the right module with the right locale.

These are:

  * **module=name**  The module to pre-select
  * **ui=name**  The Glade file to pre-select
  * **locale=name**  The locale to pre-select
  * **display=1**  If the display should be launched automatically
  * **file=file.po**  Remote PO file to download automatically

The last parameter can be very interesting for integration purposes.  
If you fill the "po_urls" setting in your instance configuration file, you can
for example provide Deckard links in your pages that would make Deckard
automatically download the PO file of the translation the user is viewing.

To sum up, you could put "view this translation in context" links everywhere.
How cool could this be?

Feel free to get in touch if you need help.  
If Deckard is not flexible enough for what you want to do, ideas are welcomed.  
Patches even more!


### Bugs/Ideas

Please report them on
[https://github.com/Malizor/deckard/issue](https://github.com/Malizor/deckard/issues)


### Licence

GNU Affero General Public License (AGPL) version 3  
Please refer to the **COPYING** file.
