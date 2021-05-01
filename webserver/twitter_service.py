import tweepy
from service import Service
import json
import configparser
import sys
import os
import logging
import logging.handlers
import time
from datetime import datetime
from threading import Thread
import sqlite3 as sq
import requests
import threading

from utils.tweet_utils import create_df

class TwitterService(Service):
    creds = {}
    query = {}
    tw_api = None

    N_QUERIES_PER_ITERATION = 5
    N_RESULTS_PER_QUERY = 50
    SLEEP_TIMEOUT = 5
    MAX_TWEET = 1000

    OUTPUT_FOLDER = 'data/twitter/output'
    LOG_FOLDER = 'data/twitter/log'

    IMAGE_FOLDER = "data/images"

    def dumps(self):
        print(self.tw_api)
        if (self.errors != {}):
            return {
                "name": self.name,
                "error": str(self.errors)
            }
        else:
            return {
                "name": self.name,
                "creds": self.creds,
                "query": self.query,
                "twitter_api": self.tw_api != None
            }

    def buildQuery(self):  #suddivido le keywords per lingua
        query = ""
        for keyword in [x.strip() for x in self.query["keywords"].split(',')]:
            if query:
                query += 'OR' 
            query += '"' + keyword + '"'    
        self.query['query'] = query
        print(query)

    def try_creds(self):
        auth = tweepy.OAuthHandler(self.creds['cons_key'], self.creds['cons_sec'])
        auth.set_access_token(self.creds['acc_tok'], self.creds['acc_sec'])
        self.tw_api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        try:
            self.tw_api.verify_credentials()
        except Exception as e:
            self.tw_api = None
            self.errors = e

    def set_args(self, args):
        if args["type"] == "creds":
            self.creds = args
            return self.try_creds()
        if args["type"] == "keyword":
            self.query = args
            self.buildQuery()

    def download_images(self, images):
        for img in images:
            image = requests.get(img).content
            hash_image = str(abs(hash(img)))
            with open(self.IMAGE_FOLDER + '/' + hash_image, "wb") as file:
                file.write(image)

    def tweet_to_pd_to_sqlite(self, tweet):
        conn = sq.connect(self.db_path)
        df = create_df(tweet, {})
        df = df.applymap(str)
        images = df["media_url"]
        self.download_images(images)
        self.download_images(images.to_list())
        cur = conn.cursor()
        df.to_sql(self.table_name, conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

        images_path = []
        for img in images:
            hash_image = str(abs(hash(img)))
            images_path.append("http://localhost:8080/images/" + hash_image)
        
        self.send(json.dumps(images_path), type="image")
        self.send("Added {} tweets to database".format(len(df)))
        self.send(df.to_json(), type="tweet")

    def run(self):
        try:
            if not os.path.exists(self.OUTPUT_FOLDER):
                os.makedirs(self.OUTPUT_FOLDER)
            if not os.path.exists(self.LOG_FOLDER):
                os.makedirs(self.LOG_FOLDER)
        except Exception as e:
            self.errors = e
            return 

        self.send("Launching the twitter crawler module", type="info")

        program_start_t = time.time()
        # logger.info('Crawling started')
        max_id = None
        since_id = None
        run = True
        start_date_obj = datetime.strptime(self.query['start'], "%Y-%m-%d")
        final_date_obj = datetime.strptime(self.query['end'], "%Y-%m-%d")
        n_iteration = 1
        total_n_tweets = 0
        
        apercu = False   

        while(run):
            #QUERY TWITTER SEARCH API    
            self.send('Iteration {0} - crawling Twitter Search API: QUERY<{1}>, FINAL_DATE<{2}>, MAX_ID<{3}>'.format(n_iteration, self.query["query"], self.query["end"], max_id))

            tweets = []
            try:
                for i in range(1,self.N_QUERIES_PER_ITERATION+1):
                    if not max_id:
                        new_tweets = self.tw_api.search(q=self.query["query"], count=self.N_RESULTS_PER_QUERY, result_type='recent', tweet_mode='extended', until=self.query["end"])
                    else:
                        new_tweets = self.tw_api.search(q=self.query["query"], count=self.N_RESULTS_PER_QUERY, result_type='recent', max_id=str(max_id - 1), tweet_mode='extended')

                    self.send('Iteration {0} - query: {1}, number of tweets: {2}'.format(n_iteration, i, len(new_tweets)))
                    
                    if not new_tweets:
                        break
                    tweets += new_tweets
                    
                    max_id = new_tweets[-1].id

                self.send('Iteration {0} - total number of retrieved tweets: {1}'.format(n_iteration,len(tweets)))

            except tweepy.TweepError as e:
                self.send('Iteration {0} - Twitter error (exception raised): {1}'.format(n_iteration, e.reason), type="error")
                return 

            #BETWEEN ITERATIONS A SLEEP TIME IS REQUIRED TO AVOID BAN
            def sleepFunc(i):
                time.sleep(i)

            sleep_t = Thread(target=sleepFunc, args=(self.SLEEP_TIMEOUT,))
            sleep_t.start()

            #CHECK ZERO RESULTS 
            if not tweets:
                self.send('Iteration {0} - no results, end of crawling', type="error")
                run = False

            #DISCARD RETWEETS
            # if self.query['ignore_retweets']:
            tweets = [x for x in tweets if not hasattr(x,'retweeted_status')]

            tweets = [x._json for x in tweets]
            self.tweet_to_pd_to_sqlite(tweets)

            # TO LOG TO FILE
            # json_object = json.dumps(tweets, indent = 4) 
            # outfile = os.path.join(self.OUTPUT_FOLDER,'{0}.json'.format(n_iteration))
            # tmp_outfile = outfile + "~"
            # with open(tmp_outfile,'w') as f: 
            #     f.write(json_object)
            # os.rename(tmp_outfile, outfile)     
            # TO LOG TO FILE

            #CHECK TOTAL NUMBER OF RESULTS 
            total_n_tweets += len(tweets)
            self.send('Iteration {0} - total number of tweets retrieved so far: {1}'.format(n_iteration,total_n_tweets))

            if total_n_tweets >= self.MAX_TWEET:
                self.send('Iteration {0} - reached maximum number of results, end of crawling'.format(n_iteration))
                run = False
            
            #WAIT FOR TIMEOUT THREAD TO COMPLETE BEFORE MOVING TO THE NEXT ITERATION
            sleep_t.join()
            n_iteration += 1