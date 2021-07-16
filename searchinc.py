import os
import json
import shlex
import random
import tempfile
import re
import pickle
import urllib
import http
import http.cookiejar
import sys

PKG_INSTALL_DIR = os.path.dirname(os.path.realpath(__file__))


def get_plugin_data_directory(pluginId):
    _remove_plugin_data()

    pluginDirectory = PKG_INSTALL_DIR + '/../plugin_data/' + pluginId
    if not os.path.exists(pluginDirectory):
        oldmask = os.umask(0)
        os.makedirs(pluginDirectory, 0o755)
        os.umask(oldmask)
    return pluginDirectory


def load_local_cache(cache_path):
    try:
        with open(cache_path, 'r') as f:
            jsonResult = json.loads(f.read())
            return jsonResult
    except:
        return None


def http_get_download(url, filepath):
    result = None
    timeouts = 30
    header = {
        r'user-agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_1; de-de) AppleWebKit/527+ (KHTML, like Gecko) Version/3.1.1 Safari/525.20',
    }

    cookie = http.cookiejar.LWPCookieJar()
    use_cookie = False
    if 'cookie_path' in globals():
        global cookie_path
        if os.path.exists(cookie_path):
            use_cookie = True

    try:
        if use_cookie:
            cookie.load(cookie_path, ignore_discard=True, ignore_expires=True)

        handler = urllib.request.HTTPCookieProcessor(cookie)
        opener = urllib.request.build_opener(handler)
        request = urllib.request.Request(url=url, headers=header, method='GET')

        response = opener.open(request, timeout=timeouts)
        result = response.read().decode('utf-8')

        if use_cookie:
            cookie.save(filename=cookie_path, ignore_discard=True, ignore_expires=True)

    except urllib.error.HTTPError as http_e:
        if http_e.code == 404:
            response_obj = json.loads(http_e.read().decode())
            if response_obj.get('status_code') == 34:
                # there's a situation that tvshow can find info,
                # but episode can't find info at certain episodes
                # so we still need process goes on, we return false
                return False
        sys.exit()

    except Exception:
        # unexpected error
        sys.exit()

    if(not result):
        return False

    with open(filepath, 'w') as f:
        f.write(result)

    return True


def parse_year(date_string):
    # input should be '2008' or 2008 or '2008-01-03'
    if type(date_string) == int:
        return date_string

    try:
        year = (int)(date_string.split('-', 1)[0])
    except:
        year = 0
    return year


def get_guessing_names(title, allowguess):
    if not allowguess:
        return [title]

    title_list = [title, _pure_lang_text(title, False)]
    engTitle = _pure_lang_text(title, True)

    if not engTitle:
        engTitle = title

    effective_word_count = _get_effective_word_count(engTitle)

    if 2 <= effective_word_count:
        title_list += [engTitle]

    if 3 <= effective_word_count:
        right_cut = _cut_string(engTitle, 1, True)
        left_cut = _cut_string(engTitle, 1, False)
        title_list += [right_cut, left_cut]

    if 4 <= effective_word_count:
        two_side_cut = _cut_string(_cut_string(engTitle, 1, False), 1, True)
        right_cut = _cut_string(engTitle, 2, True)
        left_cut = _cut_string(engTitle, 2, False)
        title_list += [two_side_cut, right_cut, left_cut]

    if 6 <= effective_word_count:
        two_side_cut = _cut_string(_cut_string(engTitle, 2, False), 2, True)
        title_list += [two_side_cut]

    return title_list


def create_cookie_file():
    tmpfile = tempfile.NamedTemporaryFile('w+t', prefix='plugin_cookie_', dir='/tmp', delete=False)
    path = tmpfile.name

    cookie = http.cookiejar.LWPCookieJar()
    cookie.save(filename=path, ignore_discard=True, ignore_expires=True)
    global cookie_path
    cookie_path = path
    return path


def delete_cookie_file(cookie_file):
    if os.path.exists(cookie_file):
        os.remove(cookie_file)


def _remove_plugin_data():
    randval = random.randrange(0, 1000)
    if randval != 0:
        return
    path = PKG_INSTALL_DIR + '/plugin_data/'
    if not os.path.exists(path):
        return

    cmd = '/usr/bin/find ' + shlex.quote(path) + ' -mtime +1 -delete'
    os.system(cmd)


def _pure_lang_text(text, only_english):
    all_num = True
    token = []
    data = [x for x in text.split(' ') if x]

    for term in data:
        containCharResult = re.search('[a-z]', term, re.IGNORECASE)
        containDigitResult = re.search('[0-9]', term, re.IGNORECASE)
        if (containCharResult != None) and (containDigitResult != None):
            # char and digit like 'hi123' would be ignore
            continue

        allDigitResult = re.search('^[0-9]+$', term, re.IGNORECASE)
        if allDigitResult != None:
            # pure digit is accept
            token.append(term)
            continue

        allCharResult = re.search('^[a-z]+$', term, re.IGNORECASE)
        if only_english and (allCharResult != None):
            # pure english char
            all_num = False
            token.append(term)
            continue

        if (not only_english) and (allCharResult == None):
            # not pure english char, like cht, jpn or sympol
            all_num = False
            token.append(term)
            continue

    if all_num:
        return ''
    return ' '.join(token)


def _get_effective_word_count(token):
    filter = ['a', 'an', 'the', 'of', 'in', 'on', 'at', 'for', 'by']

    if not isinstance(token, list):
        token = [x for x in token.split(' ') if x]

    count = 0
    for term in token:
        if term.lower() in filter:
            continue
        count += 1
    return count


def _cut_string(text, cut_count, cut_from_right):
    token = [x for x in text.split(' ') if x]
    origWords = _get_effective_word_count(token)
    newWords = origWords

    while (len(token) > 1) and (cut_count > (origWords - newWords)):
        if cut_from_right:
            token.pop()
        else:
            token.pop(0)
        newWords = _get_effective_word_count(token)
    return ' '.join(token)
