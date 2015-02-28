#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
Wololo

Post one or a serial of urls to a Wallabag instance

Usage:
    wololo post [<url>] [--wurl=<WALLABAG_url>] [--login=<username>] [--password=<psswd>]
    wololo spost [<url_list>] [--wurl=<WALLABAG_url>] [--login=<username>] [--password=<psswd>]

Options:
  -h --help       Show this screen.
  --version       Show version.
"""

import os
import sys
import getpass
import cookielib

import mechanize

from docopt import docopt

def ask(subject,passw=False):
    try:
        if passw:
            info = getpass.getpass(prompt="Type your {0} < ".format(subject))
        else:
            info = raw_input("Type your {0} < ".format(subject))

        if info == "":
            print ("Missing info: {0}".format(subject))
            sys.exit(1)

        return info
    except KeyboardInterrupt:
        return False

def post(wurl,url,login,password):
    if "framabag.org" in wurl:
        wurl = 'https://framabag.org/u/{0}'.format(login)

    # Browser
    br = mechanize.Browser()

    # Enable cookie support for urllib2
    cookiejar = cookielib.LWPCookieJar()
    br.set_cookiejar(cookiejar)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = [
            (
                'User-agent',
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'
            )
    ]

    # authenticate
    br.open(wurl)
    br.select_form(name="loginform")
    br['login'] = login
    br['password'] = password
    br.submit()

    # post the url
    formcount=0

    for form in br.forms():
      if str(form.attrs["id"]) == "bagit-form-form":
        break

      formcount=formcount+1

    br.select_form(nr=formcount)

    br['plainurl'] = url
    br.submit()

if __name__ == "__main__":
    arguments = docopt(__doc__, version='0.1')

    CURDIR = "{0}{1}".format(os.path.realpath(os.curdir),os.sep)

    for arg in ["post","spost"]:
        if arguments[arg]:
            operation,valid = arg,True

    if valid:
        DO = True

        # Si l’url/la liste d’url n’existe pas, rien ne sera envoyé.
        if operation == "post":
            if arguments["<url>"] is None:
                URL = False
            else:
                URL = arguments["<url>"]

        if operation == "spost":
            if arguments["<url_list>"] is None:
                URL = False
            else:
                URL = os.path.realpath(arguments["<url_list>"])

        # Analyse des arguments

        if URL:
            ask_for_wurl = False
            ask_for_login = False
            ask_for_password = False

            if arguments["--wurl"] is None:
                ask_for_wurl = True
            else:
                WALLABAG_URL = arguments["--wurl"]

            if arguments["--login"] is None:
                ask_for_login = True
            else:
                LOGIN = arguments["--login"]

            if arguments["--password"] is None:
                ask_for_password = True
            else:
                PASSWORD = arguments["--password"]

            # Demande des infos manquantes

            if ask_for_wurl: WALLABAG_URL = ask("wallabag instance url")
            if ask_for_login: LOGIN = ask("login")
            if ask_for_password: PASSWORD = ask("password",passw=True)

            if operation == "post":
                if DO and URL:
                    post(WALLABAG_URL,URL,LOGIN,PASSWORD)

                    sys.exit(0)

            if operation == "spost":
                try:
                    if DO and URL:
                        with open(URL,"r") as urlist:
                            for line in urlist:
                                line = line.rstrip()
                                print ("Posting {0}…".format(line))
                                post(WALLABAG_URL,line,LOGIN,PASSWORD)

                        sys.exit(0)

                except IOError:
                    print ("The url list doen't exists."); sys.exit(1)

        else:
            if operation == "post": print ("No url argument.")
            if operation == "spost": print ("No url_list argument.")

            sys.exit(1)

# vim:set shiftwidth=4 softtabstop=4:
