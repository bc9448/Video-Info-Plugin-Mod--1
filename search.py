import argparse
import html
import os
import json
import copy
import re
import util_themoviedb
import searchinc
import constant


def _plugin_run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help='json string')
    parser.add_argument("--lang", type=str, required=True, default=None, help='enu|cht|...')
    parser.add_argument("--type", type=str, required=True, default=None, help='movie|tvshow|...')
    parser.add_argument("--limit", type=int, default=1, help='result count')
    parser.add_argument("--allowguess", type=bool, default=True)
    parser.add_argument("--apikey", type=str, default='')

    # unknownPrm is useless, just for prevent error when unknow param inside
    args, unknownPrm = parser.parse_known_args()

    argv_input = json.loads(args.input)
    argv_lang = args.lang
    argv_type = args.type
    argv_limit = args.limit
    argv_allowguess = args.allowguess
    argv_apikey = args.apikey

    if argv_apikey:
        os.environ["METADATA_PLUGIN_APIKEY"] = argv_apikey

    cookie_path = searchinc.create_cookie_file()

    result = None
    success = True
    error_code = 0
    try:
        if argv_type == 'movie_similar':
            result = _similar(argv_input, argv_lang, argv_type, argv_limit)
        else:
            result = _process(argv_input, argv_lang, argv_type, argv_limit, argv_allowguess)

    except SystemExit as query_e:
        error_code = constant.ERROR_PLUGIN_QUERY_FAIL
        success = False

    except Exception as e:
        error_code = constant.ERROR_PLUGIN_PARSE_RESULT_FAIL
        success = False

    searchinc.delete_cookie_file(cookie_path)
    _process_output(success, error_code, result)


def _process(input_obj, lang, media_type, limit, allowguess):
    title = input_obj['title']
    year = _get_year(input_obj)

    season = input_obj['season'] if 'season' in input_obj else 0
    episode = input_obj['episode'] if 'episode' in input_obj else None

    # search
    query_data = []
    titles = searchinc.get_guessing_names(title, allowguess)

    for oneTitle in titles:
        if not oneTitle:
            continue

        query_data = util_themoviedb.search_media(oneTitle, lang, limit, media_type, year)

        if 0 < len(query_data):
            break
    return _get_metadata(query_data, lang, media_type, season, episode, limit)


def _similar(input_obj, lang, media_type, limit):
    item_id = int(input_obj['tmdb_id']) if 'tmdb_id' in input_obj else -1

    if (0 > item_id):
        return []
    return _get_similar_movies([{'id': item_id, 'collection_id': -1, 'lang': lang}], lang, limit)


def _get_year(input_obj):
    year = 0

    if 'original_available' in input_obj:
        year = searchinc.parse_year(input_obj['original_available'])

    if 'extra' in input_obj:
        extraItem = input_obj['extra']
        if 'tvshow' in extraItem and 'original_available' in extraItem['tvshow']:
            year = searchinc.parse_year(extraItem['tvshow']['original_available'])
    return year


def _get_metadata(query_data, lang, media_type, season, episode, limit):
    result = []
    for item in query_data:
        if item['lang'] != lang:
            continue

        media_data = None

        if media_type == 'movie':
            media_data = util_themoviedb.get_movie_detail_data(item['id'], item['lang'], constant.DEFAULT_EXPIRED_TIME)
        elif media_type == 'tvshow' or media_type == 'tvshow_episode':
            media_data = util_themoviedb.get_tv_detail_data(item['id'], item['lang'])
        else:
            return []

        if not media_data:
            continue

        if media_type == 'movie':
            result.append(_parse_movie_info(media_data))

        elif media_type == 'tvshow':
            result.append(_parse_tvshow_info(media_data))

        elif media_type == 'tvshow_episode':
            episode_data = util_themoviedb.get_tv_episode_detail_data(media_data['id'], lang, season, episode)
            result.extend(_parse_episodes_info(media_data, episode_data, season, episode))
    
        if limit <= len(result):
            result = result[:limit]
            break

    return result


def _get_similar_movies(query_data, lang, limit):
    result = []
    ids = []

    for item in query_data:
        if item['lang'] != lang:
            continue

        if 'collection_id' in item:
            if 0 >= item['collection_id']:
                item['collection_id'] = _get_collection_id(item['id'], item['lang'])

            if 0 < item['collection_id']:
                collection_response = util_themoviedb.get_movie_collection_data(item['collection_id'], item['lang'])

                if collection_response:
                    result, ids = _parse_similar_data_to_result_and_ids(
                        collection_response['parts'], limit, result, ids)
                    if len(result) >= limit:
                        break
        page = 1
        while True:
            similar_response = util_themoviedb.get_movie_similar_data(item['id'], lang, page)

            if not similar_response:
                break

            result, ids = _parse_similar_data_to_result_and_ids(similar_response['results'], limit, result, ids)

            if len(result) >= limit:
                break

            if similar_response['page'] >= similar_response['total_pages']:
                break

            page = similar_response['page'] + 1

        if len(result) >= limit:
            break
    return result


def _get_collection_id(item_id, lang):
    movie_data = util_themoviedb.get_movie_detail_data(item_id, lang, constant.DEFAULT_LONG_EXPIRED_TIME)
    if not movie_data:
        return -1

    if movie_data.get('belongs_to_collection') and 'id' in movie_data['belongs_to_collection']:
        return movie_data['belongs_to_collection']['id']

    return -1


def _parse_similar_data_to_result_and_ids(movies, limit, result, ids):
    # use for parsing each item in similar_response['results'] or collection_response['parts']

    for movie in movies:
        movie_id = movie['id']
        movie_title = movie['title']

        if movie_id in ids:
            continue

        data = copy.deepcopy(constant.MOVIE_SIMILAR_DATA_TEMPLATE)
        data['title'] = movie_title
        data['id'] = movie_id

        result.append(data)
        ids.append(movie_id)

        if len(result) >= limit:
            break
    return result, ids


def _parse_movie_info(movie_data):
    data = copy.deepcopy(constant.MOVIE_DATA_TEMPLATE)

    data['title'] = movie_data['title']
    data['original_available'] = movie_data['release_date']
    data['tagline'] = movie_data['tagline']
    data['summary'] = movie_data['overview']
    data['certificate'] = _parse_movie_certificate_info(movie_data)
    data['genre'] = _parse_genre(movie_data)

    actor, director, writer = _get_cast_info(movie_data['credits'])
    data['actor'] = actor
    data['director'] = director
    data['writer'] = writer

    data = _set_data_value(data, ['extra', constant.PLUGINID, 'reference', 'themoviedb'], movie_data['id'])
    data = _set_data_value(data, ['extra', constant.PLUGINID, 'reference', 'imdb'], movie_data['imdb_id'])

    if movie_data['vote_average']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'rating', 'themoviedb'], movie_data['vote_average'])

    if movie_data['poster_path']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'poster'], [
                               constant.BANNER_URL + movie_data['poster_path']])

    if movie_data['backdrop_path']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'backdrop'], [
                               constant.BACKDROP_URL + movie_data['backdrop_path']])

    if movie_data['belongs_to_collection'] and ('id' in movie_data['belongs_to_collection']):
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'collection_id',
                                      'themoviedb'], movie_data['belongs_to_collection']['id'])
    return data


def _parse_tvshow_info(tv_data):
    data = copy.deepcopy(constant.TVSHOW_DATA_TEMPLATE)

    data['title'] = tv_data['name']
    data['original_available'] = tv_data['first_air_date']
    data['summary'] = tv_data['overview']

    if tv_data['poster_path']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'poster'], [
                               constant.BANNER_URL + tv_data['poster_path']])
    if tv_data['backdrop_path']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'backdrop'], [
            constant.BACKDROP_URL + tv_data['backdrop_path']])
    return data

def _parse_episodes_info(tv_data, episode_data, season, episode):
    parse_info_result = []
    if episode != None:
        parse_info_result.append(_parse_episode_info(tv_data, episode_data, season, episode))
    elif (episode_data != None) and ('episodes' in episode_data):
        episodes = episode_data['episodes']
        for episode_object in episodes:
            parse_info_result.append(_parse_episode_info(tv_data, episode_object, season, episode))
    return parse_info_result

def _parse_episode_info(tv_data, episode_data, season, episode):
    data = copy.deepcopy(constant.TVSHOW_EPISODE_DATA_TEMPLATE)

    data['title'] = tv_data['name']
    data['season'] = season
    data['episode'] = episode_data['episode_number'] if episode_data != None and 'episode_number' in episode_data else episode

    tvshow_data = _parse_tvshow_info(tv_data)
    data = _set_data_value(data, ['extra', constant.PLUGINID, 'tvshow'], tvshow_data)

    if not episode_data:
        return data

    data['tagline'] = episode_data['name']
    data['original_available'] = episode_data['air_date']
    data['summary'] = episode_data['overview']
    data['certificate'] = _parse_tv_certificate_info(tv_data)
    data['genre'] = _parse_genre(tv_data)

    if 'credits' in episode_data:
        actor, director, writer = _get_cast_info(episode_data['credits'])
    else:
        actor, director, writer = _get_cast_info(episode_data)

    data['actor'] = actor
    data['director'] = director
    data['writer'] = writer

    if episode_data['still_path']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'poster'], [
                               constant.BANNER_URL + episode_data['still_path']])

    data = _set_data_value(data, ['extra', constant.PLUGINID, 'reference', 'themoviedb_tv'], tv_data['id'])
    data = _set_data_value(data, ['extra', constant.PLUGINID, 'reference', 'imdb'], tv_data['external_ids']['imdb_id'])
    data = _set_data_value(data, ['extra', constant.PLUGINID, 'rating', 'themoviedb_tv'], tv_data['vote_average'])
    return data


def _set_data_value(data, key_list, value):
    if not value:
        return data

    now_data = data
    for attr in key_list[:-1]:
        if attr not in now_data:
            now_data[attr] = {}
        now_data = now_data[attr]

    now_data[key_list[-1]] = value
    return data


def _get_cast_info(cast_data):
    actor = []
    director = []
    writer = []

    if 'cast' in cast_data:
        for item in cast_data['cast']:
            if item['name'] not in actor:
                actor.append(item['name'])

    # only for tvshow episode
    if 'guest_stars' in cast_data:
        for item in cast_data['guest_stars']:
            if item['name'] not in actor:
                actor.append(item['name'])

    if 'crew' in cast_data:
        for item in cast_data['crew']:
            if (item['department'] == 'Directing') and (item['name'] not in director):
                director.append(item['name'])

            if (item['department'] == 'Writing') and (item['name'] not in writer):
                writer.append(item['name'])
    return actor, director, writer

def _parse_movie_certificate_info(movie_data):
    release_data = movie_data['releases']

    certificate = {}
    for item in release_data['countries']:
        if not item['certification']:
            continue

        if item['iso_3166_1'].lower() == 'us':
            return item['certification']

        certificate[item['iso_3166_1']] = item['certification']

    if len(certificate) == 0:
        return None

    return list(certificate.values())[0]


def _parse_tv_certificate_info(tv_data):
    certificate = {}

    for item in tv_data['content_ratings']['results']:
        if not item['rating']:
            continue

        if item['iso_3166_1'].lower() == 'us':
            return item['rating']

        certificate[item['iso_3166_1']] = item['rating']

    if len(certificate) == 0:
        return None

    return list(certificate.values())[0]


def _parse_genre(media_data):
    genre = []
    for item in media_data['genres']:
        if item['name'] not in genre:
            genre.append(item['name'])
    return genre


def _process_output(success, error_code, datas):
    result_obj = {}
    if success:
        result_obj = {'success': True, 'result': datas}
    else:
        result_obj = {'success': False, 'error_code': error_code}

    json_string = json.dumps(result_obj, ensure_ascii=False, separators=(',', ':'))
    json_string = html.unescape(json_string)
    print(json_string)


if __name__ == "__main__":
    _plugin_run()
