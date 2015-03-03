"""
Functions for getting tweets from Twitter (via REST API), file, and database

@auth dpb and yns
@date 2/17/2015
"""

from bson.json_util import loads
from tweepy import Cursor, TweepError
from json_util import ConcatJSONDecoder

def _check_limit(limit):
    """Checks common 'limit' param to see if is int. Exception if not"""
    if type(limit) != int:
        raise Exception("Limit ({0}) must be an integer".format(limit))

def query_tweets(api, query, limit=None, languages=None):
    """
    Queries twitter REST API for tweets matching given twitter search 'query'.
    Takes an authenticated api object (API or APIPool), a query string, an optional
    limit for number of tweets returned, and an optional list of languages to
    further filter results.
    Returns a cursor (iterator) over Tweepy status objects (not native JSON docs)
    """
    cursor = Cursor(api.search, q=query, include_entities=True, lang=languages)
    if limit:
        _check_limit(limit)
        return cursor.items(limit)
    return cursor.items()

def user_tweets(api, user_id=None, screen_name=None, limit=None):
    """
    Queries Twitter REST API for user's tweets. Returns as many as possible, or
    up to given limit.
    Takes an authenticated API object (API or APIPool), one of user_id or screen_name 
    (not both), and an optional limit for number of tweets returned.
    Returns a cursor (iterator) over Tweepy status objects
    """
    if not (user_id or screen_name):
        raise Exception("Must provide one of user_id or screen_name")
    if user_id:
        cursor = Cursor(api.user_timeline, user_id=user_id)
    elif screen_name:
        cursor = Cursor(api.user_timeline, screen_name=screen_name)
    if limit:
        _check_limit(limit)
        return cursor.items(limit)
    return cursor.items()

def place_tweets(api, place_list=None, query="", granularity=None, limit=None):
    """
    Queries Twitter REST API for tweets based on a name of a place or a list of place names.
    Takes an authenticated API object(API or APIPool not both), and an optional 
    limit for the number of tweets returned.
    Takes a place_list of names of places in the world. 
    It is crucial to note that for a place_list the limit applies to each
    location, and not over all locations. 
    For example a query to ["Kyiv", "San Francisco"] would have a limit of 5
    for the first query to Kyiv and 5 for the second query to San Francisco.
    Returns an array whose elements are iterators over the elements of each 
    place in the original place_list.
    ["Kyiv", "San Francisco"] returns[Kyiv_Iterator_Obj, SanFrancisco_Iterator_Obj]
    """
    locations_iterators = []
    if not (place_list):
        raise Exception("Hey hotshot slow down! You're missing a place_list input.")

    for place in place_list:
        placeid_search = api.geo_search(query=place, max_results=limit, granularity=granularity)
        place_id = placeid_search[0].id # 0 gets the most likely place, not error proof
        tweets_from_place = query_tweets(api, query=query+"&place:%s" % place_id, limit=limit)
        locations_iterators.append(tweets_from_place)

    return iter(locations_iterators)

def georadius_tweets(api, georadius_list=None, query="", limit=None):
    """
    Queries Twitter REST API for tweets within a radius of two coordinates.
    Takes an authenticated API object (API or APIPool), and a geo-object which
    two coordinates and a radius or a list of geo-objects , and a limit on 
    the number of queries for each georadius.
    Returns a list whose elements are iterators over the results from each
    provided georadius.
    """
    locations_iterators = []
    if not(georadius_list):
        raise Exception("Hey city slicker! You're missing a georadius_list input.")
    
    for georadius in georadius_list:
        for i in range(0, len(georadius)):
            georadius[i] = str(georadius[i])

        tweets_from_place = query_tweets(api, query=query+"&geocode:%s" % ",".join(georadius), limit=limit)
        locations_iterators.append(tweets_from_place)

    return iter(locations_iterators)

def tweets_from_file(tweetfile):
    """
    Returns a list of tweets read from given file. Tweets are dicts representing json of 
    file contents. For a less-memory intensive version, consider the tweet_from_file_IT() 
    function.
    Note: will not check validity of tweet. Will simply return dict representations of
    JSON entities in the file
    """
    with open(tweetfile) as handle:
        tweets = loads(handle.read(), cls=ConcatJSONDecoder)
    return tweets

def tweets_from_file_IT(tweetfile):
    """
    Returns an iterator for tweets in given tweetfile. Tweets are considered dict
    representations of JSON in given tweetfile
    """
    with open(tweetfile) as handle:
        for line in handle:
            yield loads(line.strip())

def tweets_from_db():
    """"""
    raise NotImplementedError()
