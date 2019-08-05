import requests
import time
from collections import Counter
import json
import datetime
import sqlite3

class SubredditStatistics():
    def __init__(self, subreddit_name, database_name=':memory:', database=False):
        self.subreddit_name = subreddit_name
        self.database = database

        # Check if subreddit exist
        if not self.exist:
            print(f"{subreddit_name} does not exists.")
            exit()

        if not database:
            self.create_json_files()
        else:
            self.create_database(database_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.database:
            self.conn.close()

    def create_json_files(self):
        with open(f'users_{self.subreddit_name}.json', 'w') as f:
            data = {}
            json.dump(data, f)
        
        with open(f'words_{self.subreddit_name}.json', 'w') as f:
            data = {'words':{}, "posts": {"number": 0, "spoiler": 0}, "comments": {"number": 0, "spoiler": 0}, 
            'activity':{str(k):0 for k in range(24)}}
            json.dump(data, f)

    def create_database(self, name):
        # Create connection and cursor
        self.conn = sqlite3.connect(name)
        self.c = self.conn.cursor()

        # Create Tables
        self.c.execute("""CREATE TABLE words(
        word text,
        count integer
        )""")

        self.c.execute("""CREATE TABLE users(
            user text,
            post integer,
            comment integer
            )""")

        self.c.execute("""CREATE TABLE submissions(
            type text,
            count integer,
            spoiler integer
            )""")

        self.c.execute(""" CREATE TABLE  sub_times(
            hour text,
            count integer
            )""")

        self.conn.commit()

        # Create row for number of posts and comments with values 0
        self.insert_post()
        self.insert_comment()
        self.insert_hours()


    @property
    def exist(self):
        api = f'https://api.pushshift.io/reddit/search/submission/?subreddit={self.subreddit_name}'

        response = requests.get(api)

        if not response.ok:
            raise('Something went wrong! There is a problem either with your internet or with a server, please try again later.')

        return bool(response.json()['data'])

    def download_and_save_statistics(self):
        # Download submissions
        date_submissions = int(time.time())
        while True:
            data_chunk = []
            submissions = self.download_500_submissions(date_submissions)

            # Empty list means that there are no older posts
            if not submissions:
                break

            # Set new before date as last post date - 1s
            date_submissions = submissions[-1]['created_utc'] - 1

            print(f" Now downloading posts from date: {datetime.datetime.fromtimestamp(date_submissions).strftime('%Y-%m-%d %H:%M:%S')}")

            # Proccess data
            for sub in submissions:
                data = self.process_data(sub, 'sub')
                data_chunk.append(data)

            if self.database:
                pd = self.pack_data(data_chunk, 'post')
                self.write_to_database(pd, 'post')
            else:
                self.write_to_file(data_chunk, 'posts')

        # Download comments
        date_commnets = int(time.time())
        while True:
            data_chunk = []
            comments = self.download_500_comments(date_commnets)

            # Empty list means that there are no older comments
            if not comments:
                break

            # Set new before date as last post date - 1s
            date_commnets = comments[-1]['created_utc'] - 1

            print(f" Now downloading comments from date: {datetime.datetime.fromtimestamp(date_commnets).strftime('%Y-%m-%d %H:%M:%S')}")

            for sub in comments:
                data = self.process_data(sub, 'com')
                data_chunk.append(data)

            if self.database:
                pd = self.pack_data(data_chunk, 'comment')
                self.write_to_database(pd, 'comment')
            else:
                self.write_to_file(data_chunk, 'comments')

    def download_500_submissions(self, before):
        api = f'https://api.pushshift.io/reddit/search/submission/?subreddit={self.subreddit_name}&before={before}&size=500&fields=selftext,author,created_utc,spoiler'

        return requests.get(api).json().get('data', {})
    
    def download_500_comments(self, before):
        api = f'https://api.pushshift.io/reddit/search/comment/?subreddit={self.subreddit_name}&before={before}&size=500&fields=body,author,created_utc'

        return requests.get(api).json().get('data', {})

    def write_to_file(self, data, data_type):
        old_data_words:dict
        old_data_users:dict

        with open(f'words_{self.subreddit_name}.json', 'r') as f_words:
            old_data_words = json.load(f_words)
        with open(f'users_{self.subreddit_name}.json', 'r') as f_users:
            old_data_users = json.load(f_users)

        with open(f'words_{self.subreddit_name}.json', 'w') as f_words:
            with open(f'users_{self.subreddit_name}.json', 'w') as f_users:
                # Get one submission/comment
                for sub in data:
                    # Add words
                    for word, count in sub['words'].items():
                        old_data_words['words'][word] = old_data_words['words'].get(word, 0) + count

                    # Add posts spoiler
                    if sub['spoiler']:
                        old_data_words[data_type]['spoiler'] += 1

                    # Add user data
                    user_data = old_data_users.get(sub['author'], {'posts':0, 'comments':0})
                    user_data[data_type] += 1
                    old_data_users[sub['author']] = user_data

                    # Add submission time
                    old_data_words['activity'][sub['hour']] += 1

                # Add number of posts/comments
                old_data_words[data_type]['number'] += len(data)

                json.dump(old_data_words, f_words)
                json.dump(old_data_users, f_users)
    
    def write_to_database(self, data, data_type):
        # Update word count
        for word, count in data['words'].items():
            old_word_count = self.get_word_count(word)

            # If word inside database update if not create new row
            if old_word_count is not None:
                self.update_word_count(word, old_word_count[1]+count)
            else:
                self.insert_new_word(word, count)

        # Update user count
        for user, user_data in data['users'].items():     
            old_user_data = self.get_user_count(user)

            # If user not in database create row
            if old_user_data is None:
                self.insert_new_user(user)
                old_user_data = self.get_user_count(user)

            # Get old user data
            post_count = old_user_data[1]
            comment_count = old_user_data[2]

            # Update user data
            if data_type == 'post':
                post_count += user_data['post']
            else:
                comment_count += user_data['comment']
            
            self.update_user_count(user, post_count, comment_count)
        

        # Update submission and spoiler count
        old_sub_data = self.get_submission_count(data_type)

        if data_type == 'post':
            self.update_post_count(data['submissions']['post']['count'] + old_sub_data[1], data['submissions']['post']['spoiler'] + old_sub_data[2])
        else:
            self.update_comment_count(data['submissions']['comment']['count'] + old_sub_data[1])
        
        # Update submission times data
        for hour, count in data['activity'].items():
            self.update_sub_time(hour, count)

        self.conn.commit()


    def process_data(self, data, data_type):
        # Basic data
        user = data.get('author', '')

        if data_type == 'sub':
            text = data.get('selftext', "").lower()
        else:
            text = data.get('body', "").lower()

        title = data.get('title', "").lower()
        spoiler = data.get('spoiler', False)

        hour = datetime.datetime.fromtimestamp(data.get('created_utc', None)).hour

        # Delete unnecessary characters
        for character in [',', '.', '^', '?', '!', '@', '#', '$', ':', ';', '/', '-', '_', '(', ')', '\n', '\\n', '"', 
            '*', '\r', '=', '&', '[', ']', '\\r', "\\", '|', '“', '”', u'\xa0', '~', u'\u200b', u'\u200f', '‘', u'\u2019']:
            text = text.replace(character, ' ')
            title = title.replace(character, ' ')

        # Get word counts
        words_text = dict(Counter(text.split(' ')))
        words_title = dict(Counter(title.split(' ')))

        # Add words counts
        for word, count in words_title.items():
            words_text[word] = words_text.get(word, 0) + count

        # Delete empty string keys and exclude some values like [removed] or links
        words = {str(k):v for k, v in words_text.items() if k and not k in ['[removed]', 'https'] and len(str(k)) < 15}

        return {'author': user, 'words': words, 'spoiler': spoiler, 'hour': str(hour)}

    def pack_data(self, data_chunk, data_type):
        packed_data = {'words':{},
                    'submissions':{'post':{'count':0, 'spoiler':0},
                                'comment':{'count':0, 'spoiler':0}},
                    'users':{},
                    'activity':{str(k):0 for k in range(24)}}

        # Loop through all submissions
        for sub in data_chunk:
            
            # Add words
            for word, count in sub['words'].items():
                packed_data['words'][word] = packed_data['words'].get(word, 0) + count
            
            # Add to submission count
            packed_data['submissions'][data_type]['count'] += 1

            # Spoiler
            if sub['spoiler']:
                packed_data['submissions'][data_type]['spoiler'] += 1

            # User data
            user_data = packed_data['users'].get(sub['author'], {'post':0, 'comment':0})
            user_data[data_type] += 1
            packed_data['users'][sub['author']] = user_data

            # Submission time
            packed_data['activity'][sub['hour']] += 1

        return packed_data

    def get_word_count(self, word):
        self.c.execute("SELECT * FROM words WHERE word=:word", {'word':word})
        return self.c.fetchone()
    
    def get_user_count(self, user):
        self.c.execute("SELECT * FROM users WHERE user=:user", {'user':user})
        return self.c.fetchone()

    def get_submission_count(self, sub_type):
        self.c.execute("SELECT * FROM submissions WHERE type=:type", {'type':sub_type})
        return self.c.fetchone()

    def update_word_count(self, word, count):
        self.c.execute("UPDATE words SET count=:count WHERE word=:word", {'count':count, 'word': word})

    def update_user_count(self, user, post, comment):
        self.c.execute("UPDATE users SET post=:post, comment=:comment WHERE user=:user", {'post': post, 'comment':comment,'user':user})

    def update_post_count(self, count, spoiler):
        self.c.execute("UPDATE submissions SET count=:count, spoiler=:spoiler WHERE type=:type", {'count':count, 'spoiler':spoiler, 'type':'post'})

    def update_comment_count(self, count):
        self.c.execute("UPDATE submissions SET count=:count WHERE type=:type", {'count':count, 'type':'comment'})
    
    def update_sub_time(self, hour, count):
        self.c.execute("UPDATE sub_times SET count=:count WHERE hour=:hour", {'count': count, 'hour': hour})

    def insert_new_word(self, word, count):
        self.c.execute("INSERT INTO words VALUES (:word, :count)", {'word':word, 'count':count})

    def insert_new_user(self, user):
        self.c.execute("INSERT INTO users VALUES (:user, 0, 0)", {'user':user})

    def insert_post(self):
        self.c.execute("INSERT INTO submissions VALUES ('post', 0, 0)")
        self.conn.commit()

    def insert_comment(self):
        self.c.execute("INSERT INTO submissions VALUES ('comment', 0, 0)")
        self.conn.commit()

    def insert_hours(self):
        for hour in range(24):
            self.c.execute("INSERT INTO sub_times VALUES (:hour, 0)", {'hour': hour})

        self.conn.commit()

if __name__ == "__main__":
    with SubredditStatistics('the100', database=False) as s:
        s.download_and_save_statistics()
