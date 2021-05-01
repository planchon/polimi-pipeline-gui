import json
import os
import pandas as pd
from langdetect import detect

def read_json_robust(file):
    """
    Read a json accounting for multiple formats.
    :param file: file path
    :return: list of tweets
    """
    with open(file) as f:
        try:
            # standard json file
            data = json.load(f)
        except Exception:
            # list of json in the same file
            f.seek(0)
            data = [json.loads(l) for l in f.readlines()]
    return data

def create_df(data, args):
    tweet_ids = set()

    tweet_id = []
    id_str = []
    created_at = []
    media_url = []
    url = []
    media_type = []
    language_code = []
    bounding_box = []
    country = []
    country_code = []
    user_loc = []
    full_text = []
    image = []
    
    for tweet in data:
        # no images in media
        if 'media' not in tweet['entities']:
            continue
        else:
            media = tweet['entities']['media'][0]
            # remove duplicate
            if media['media_url'] in media_url:
                continue


        t_id = tweet['id']
        tweet_id.append(t_id)
        url.append(f'http://twitter.com/anuuser/status/{t_id}')
        id_str.append(tweet['id_str'])
        created_at.append(tweet['created_at'])
        try:
            full_text.append(tweet['full_text'])
        except KeyError:
            full_text.append(tweet['text'])
        
        try:
            language_code.append(tweet['metadata']['iso_language_code'])
        except KeyError:
            if args.skip_language_inference:
                language_code.append('-')
            else:
                l_code = detect(full_text[-1])
                language_code.append(l_code)
        media_url.append(media['media_url'])
        image.append(abs(hash(media['media_url'])))
        media_type.append(media['type'])

        if tweet['place'] is None:
            country.append('-')
            country_code.append('-')
            bounding_box.append('[0]')
        else:
            place = tweet['place']

            country.append(place['country'])
            country_code.append(place['country_code'])
            bounding_box.append(place['bounding_box']['coordinates'][0])

        if tweet['user']['location'] is None:
            user_loc.append(tweet['user']['location'])
        else:
            user_loc.append('-')

    print (len(tweet_id) == len(id_str) == len(created_at) == len(media_url) == len(url) == len(media_type) == len(
        language_code) == len(bounding_box) == len(country) == len(country_code) == len(user_loc) == len(full_text))

    df_tweets = pd.DataFrame(
        {'id': tweet_id, 'image': image, 'id_str': id_str, 'created_at': created_at, 'media_url': media_url, 'url': url,
         'type': media_type, 'language_code': language_code,
         'bounding_box': bounding_box, 'country': country, 'country_code': country_code, 'user_loc': user_loc,
         'full_text': full_text})

    return df_tweets