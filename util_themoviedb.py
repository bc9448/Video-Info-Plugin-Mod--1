import os
import urllib
import time
import json
import searchinc
import constant


def search_media(name, lang, limit, media_type, year):
    page = 1

    if media_type == 'movie':
        search_func = _get_movie_search_data

    elif media_type == 'tvshow' or media_type == 'tvshow_episode':
        search_func = _get_tv_search_data

    else:
        return []

    search_data = search_func(name, lang, year, page)

    if not search_data.get('total_pages'):
        return []

    total_pages = search_data['total_pages']
    total_result = parse_search_data(search_data, lang, limit, media_type, year)

    while ((len(total_result) < limit) and page < total_pages):
        page += 1
        search_data = search_func(name, lang, year, page)
        one_page_result = parse_search_data(search_data, lang, limit, media_type, year)
        total_result.extend(one_page_result)

    if (0 < limit) and (limit < len(total_result)):
        total_result = total_result[0:limit]

    return total_result


def parse_search_data(search_data, lang, limit, media_type, year):
    if not search_data.get('results'):
        return []

    result = []
    for item in search_data['results']:
        data = {}
        data['id'] = item['id']

        if not _is_translation_available(data['id'], lang, media_type):
            continue

        data['lang'] = lang

        if year and 'release_date' in item:
            item_year = searchinc.parse_year(item['release_date'])
            year_diff = abs(item_year - year)

            if 2 <= year_diff and item_year:
                continue

        result.append(data)

        if (0 < limit) and (limit <= len(result)):
            break

    return result


def _get_movie_search_data(name, lang, year, page):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''
    convert_lang = _convert_to_api_lang(lang)
    nameEncode = urllib.parse.quote_plus(name)

    cache_path = searchinc.get_plugin_data_directory(
        constant.PLUGINID) + '/movie/query/' + nameEncode + '_' + str(year) + '_' + convert_lang + '_' + str(page) + '.json'

    # example: https://api.themoviedb.org/3/search/movie?api_key=xxxxx&query=harry%20potter&language=zh-TW&year=0&page=1
    url = constant.THEMOVIEDB_URL + 'search/movie?api_key=' + api_key + '&query=' + nameEncode + '&language=' + \
        convert_lang + '&year=' + str(year) + '&page=' + str(page)
    return _get_data_from_cache_or_download(url, cache_path, constant.DEFAULT_EXPIRED_TIME)


def _get_movie_translation_data(item_id):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''

    cache_path = searchinc.get_plugin_data_directory(constant.PLUGINID) + '/movie/' + str(item_id) + '/translation.json'

    # example: https://api.themoviedb.org/3/movie/671/translations?api_key=xxxxx
    url = constant.THEMOVIEDB_URL + 'movie/' + str(item_id) + '/translations?api_key=' + api_key
    return _get_data_from_cache_or_download(url, cache_path, constant.DEFAULT_EXPIRED_TIME)


def get_movie_detail_data(item_id, lang, expired_time):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''
    convert_lang = _convert_to_api_lang(lang)

    cache_path = searchinc.get_plugin_data_directory(
        constant.PLUGINID) + '/movie/' + str(item_id) + '/' + convert_lang + '.json'

    # example: https://api.themoviedb.org/3/movie/671?api_key=xxxxx&append_to_response=credits,releases&language=zh-TW
    url = constant.THEMOVIEDB_URL + 'movie/' + str(item_id) + '?api_key=' + api_key + \
        '&language=' + convert_lang + '&append_to_response=credits,releases'
    return _get_data_from_cache_or_download(url, cache_path, expired_time)


def get_movie_similar_data(item_id, lang, page):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''
    convert_lang = _convert_to_api_lang(lang)

    cache_path = searchinc.get_plugin_data_directory(
        constant.PLUGINID) + "/movie/" + str(item_id) + "/" + convert_lang + "_" + str(page) + "_similar.json"

    # example: https://api.themoviedb.org/3/movie/671/similar?api_key=xxxxx&language=zh-TW&page=1
    url = constant.THEMOVIEDB_URL + "movie/" + str(item_id) + "/similar?api_key=" + api_key + \
        '&language=' + convert_lang + '&page=' + str(page)
    return _get_data_from_cache_or_download(url, cache_path, constant.DEFAULT_LONG_EXPIRED_TIME)


def get_movie_collection_data(item_id, lang):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''
    convert_lang = _convert_to_api_lang(lang)

    cache_path = searchinc.get_plugin_data_directory(
        constant.PLUGINID) + "/movie/" + str(item_id) + "/" + convert_lang + "_collection.json"

    # example: https://api.themoviedb.org/3/collection/1241?api_key=xxxxx&language=zh-TW
    url = constant.THEMOVIEDB_URL + "collection/" + str(item_id) + '?api_key=' + api_key + '&language=' + convert_lang
    return _get_data_from_cache_or_download(url, cache_path, constant.DEFAULT_LONG_EXPIRED_TIME)


def _get_tv_search_data(name, lang, year, page):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''
    convert_lang = _convert_to_api_lang(lang)
    nameEncode = urllib.parse.quote_plus(name)

    cache_path = searchinc.get_plugin_data_directory(
        constant.PLUGINID) + '/tv/query/' + nameEncode + '_' + str(year) + '_' + convert_lang + '_' + str(page) + '.json'

    # example: https://api.themoviedb.org/3/search/tv?api_key=xxxxx&query=superman&language=zh-TW&year=0&page=1
    url = constant.THEMOVIEDB_URL + "search/tv?api_key=" + api_key + '&query=' + \
        nameEncode + '&language=' + convert_lang + '&year=' + str(year) + '&page=' + str(page)
    return _get_data_from_cache_or_download(url, cache_path, constant.DEFAULT_EXPIRED_TIME)


def get_tv_detail_data(item_id, lang):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''
    convert_lang = _convert_to_api_lang(lang)

    cache_path = searchinc.get_plugin_data_directory(
        constant.PLUGINID) + "/tv/" + str(item_id) + "/" + convert_lang + ".json"

    # example: https://api.themoviedb.org/3/tv/1403?api_key=xxxxx&append_to_response=credits,content_ratings,external_ids&language=zh-TW
    url = constant.THEMOVIEDB_URL + "tv/" + str(item_id) + '?api_key=' + api_key + '&language=' + \
        convert_lang + '&append_to_response=credits,content_ratings,external_ids'
    return _get_data_from_cache_or_download(url, cache_path, constant.DEFAULT_EXPIRED_TIME)


def get_tv_episode_detail_data(item_id, lang, season, episode):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''
    convert_lang = _convert_to_api_lang(lang)

    episode_cache_pattern = '_e' + str(episode) if episode != None else ''
    cache_path = searchinc.get_plugin_data_directory(
        constant.PLUGINID) + "/tv/" + str(item_id) + "/" + convert_lang + '_s' + str(season) + episode_cache_pattern + ".json"

    # example: https://api.themoviedb.org/3/tv/1403/season/1/episode/3?api_key=xxxxx&language=zh-TW&append_to_response=credits
    episode_url_pattern = '/episode/' + str(episode) if episode != None else ''
    url = constant.THEMOVIEDB_URL + "tv/" + \
        str(item_id) + '/season/' + str(season) + episode_url_pattern + '?api_key=' + \
        api_key + '&language=' + convert_lang + '&append_to_response=credits'
    return _get_data_from_cache_or_download(url, cache_path, constant.DEFAULT_EXPIRED_TIME)


def _get_tv_translation_data(item_id):
    api_key = os.environ['METADATA_PLUGIN_APIKEY'] if os.environ.get('METADATA_PLUGIN_APIKEY') else ''

    cache_path = searchinc.get_plugin_data_directory(constant.PLUGINID) + "/tv/" + str(item_id) + "/translation.json"

    # example: https://api.themoviedb.org/3/tv/1403/translations?api_key=xxxxx
    url = constant.THEMOVIEDB_URL + "tv/" + str(item_id) + "/translations?api_key=" + api_key
    return _get_data_from_cache_or_download(url, cache_path, constant.DEFAULT_EXPIRED_TIME)


def _get_data_from_cache_or_download(url, cache_path, expired_time):
    result = None

    if os.path.exists(cache_path):
        last_modify_time = os.path.getmtime(cache_path)

        if expired_time > (time.time()-last_modify_time):
            result = searchinc.load_local_cache(cache_path)

            if result != None:
                return result

        os.remove(cache_path)

    else:
        directory_path = os.path.dirname(cache_path)
        if not os.path.exists(directory_path):
            oldmask = os.umask(0)
            os.makedirs(directory_path, 0o755)
            os.umask(oldmask)

    download_success = searchinc.http_get_download(url, cache_path)

    if download_success:
        result = searchinc.load_local_cache(cache_path)

    return result


def _is_translation_available(item_id, lang, mediaType):
    translationData = None

    if mediaType == 'movie':
        translationData = _get_movie_translation_data(item_id)
    elif mediaType == 'tvshow' or mediaType == 'tvshow_episode':
        translationData = _get_tv_translation_data(item_id)
    else:
        return False

    if not translationData:
        return False

    translation_array = _parse_translation(translationData)
    converted_lang = _convert_to_api_lang(lang)
    if converted_lang not in translation_array:
        return False
    return True


def _parse_translation(translationData):
    langList = []
    for item in translationData['translations']:
        iso639 = item['iso_639_1']
        iso3166 = item['iso_3166_1']
        langList.append(iso639 + '-' + iso3166)
    return langList


def _convert_to_api_lang(lang):
    langDict = constant.LANGUAGE_DICT
    if lang in langDict.keys():
        return langDict[lang]

    if lang in langDict.values():
        return lang
    return None
