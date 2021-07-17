ERROR_PLUGIN_QUERY_FAIL = 1003
ERROR_PLUGIN_PARSE_RESULT_FAIL = 1004

PLUGINID = 'bc9448_themoviedb_alt'
THEMOVIEDB_URL = 'https://api.themoviedb.org/3/'
BANNER_URL = 'https://image.tmdb.org/t/p/w500'
BACKDROP_URL = 'https://image.tmdb.org/t/p/original'
DEFAULT_EXPIRED_TIME = 86400
DEFAULT_LONG_EXPIRED_TIME = 86400 * 30

LANGUAGE_DICT = {
    'chs': 'zh-CN', 'cht': 'zh-TW', 'csy': 'cs-CZ', 'dan': 'da-DK',
    'enu': 'en-US', 'fre': 'fr-FR', 'ger': 'de-DE', 'hun': 'hu-HU',
    'ita': 'it-IT', 'jpn': 'ja-JP', 'krn': 'ko-KR', 'nld': 'nl-NL',
    'nor': 'no-NO', 'plk': 'pl-PL', 'ptb': 'pt-BR', 'ptg': 'pt-PT',
    'rus': 'ru-RU', 'spn': 'es-ES', 'sve': 'sv-SE', 'trk': 'tr-TR',
    'tha': 'th-TH'
}

MOVIE_DATA_TEMPLATE = {
    'title': '',
    'tagline': '',
    'original_available': '',
    'summary': '',
    'certificate': '',
    'genre': [],
    'actor': [],
    'director': [],
    'writer': [],
    'extra': {}
}

"""
movie extra template
    'extra': {
        PLUGINID: {
            'poster': [],
            'backdrop': [],
            'reference': {
                'themoviedb': None,
                'imdb': None
            },
            'rating': {
                'themoviedb': None
            },
            'collection_id': {
                'themoviedb': -1
            }
        }
    }
"""


TVSHOW_DATA_TEMPLATE = {
    'title': '',
    'original_available': '',
    'summary': '',
    'extra': {}
}

"""
tvshow extra template
    'extra': {
        PLUGINID: {
            'poster': [],
            'backdrop': [],
        }
    }
"""


TVSHOW_EPISODE_DATA_TEMPLATE = {
    'title': '',
    'tagline': '',
    'original_available': '',
    'summary': '',
    'certificate': '',
    'genre': [],
    'actor': [],
    'director': [],
    'writer': [],
    'season': -1,
    'episode': -1,
    'extra': {}
}

"""
tvshow_episode extra template
    'extra': {
        PLUGINID: {
            'tvshow': TVSHOW_DATA_TEMPLATE,
            'poster': [],
            'reference': {
                'themoviedb_tv': None,
                'imdb': None
            },
            'rating': {
                'themoviedb_tv': None
            }
        }
    }
"""

MOVIE_SIMILAR_DATA_TEMPLATE = {
    'title': '',
    'id': -1
}
