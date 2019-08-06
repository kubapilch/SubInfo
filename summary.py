import json

class Summary():

    def __init__(self, sub_name):
        self.sub_name = sub_name

    def __enter__(self):
        try:
            self.wordsIO = open(f'words_{self.sub_name}.json', 'r')
        except IOError as e:
            print(f'I/O error({e.errno}): {e.strerror} words_{self.sub_name}.json')
            exit()

        try:
            self.usersIO = open(f'users_{self.sub_name}.json', 'r')
        except IOError as e:
            print(f'I/O error({e.errno}): {e.strerror} users_{self.sub_name}.json')
            exit()
        
        try:
            self.stop_wordsIO = open('stopwords.txt', 'r')
        except IOError as e:
            print(f'I/O error({e.errno}): {e.strerror} stopwords.txt')
            exit()
        
        self.load_data()

        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.wordsIO.close()
        self.usersIO.close()
        self.stop_wordsIO.close()

    def load_data(self):
        self.words = json.load(self.wordsIO)
        self.users = json.load(self.usersIO)
        self.stop_words = self.stop_wordsIO.read().split('\n')

    def top_commenters(self, number):
        # Get top users
        top_users = sorted(self.users.items(), key=lambda x: x[1]['comments'], reverse=True)[:number]
        
        # Display data
        print('\n-------TOP COMMENTERS-------')
        for place, user in enumerate(top_users, 1):
            print(f'{place}. {user[0]} - {user[1]["comments"]} comments')

    def top_posters(self, number):
        # Get top users
        top_users = sorted(self.users.items(), key=lambda x: x[1]['posts'], reverse=True)[:number]
        
        # Display data
        print('\n-------TOP POSTERS-------')
        for place, user in enumerate(top_users, 1):
            print(f'{place}. {user[0]} - {user[1]["posts"]} posts')

    def top_submissions(self, number):
        # Get top users
        top_users = sorted(self.users.items(), key=lambda x: x[1]['comments']+x[1]['posts'], reverse=True)[:number]
        
        # Display data
        print('\n-------TOP SUBMISSIONS-------')
        for place, user in enumerate(top_users, 1):
            print(f'{place}. {user[0]} - {user[1]["comments"]+user[1]["posts"]} submissions')

    def total_number_of_words(self):
        total_number = sum(self.words['words'].values())

        print(f'\nTotal number of words is: {total_number}')

    def top_words(self, number):
        # Sort words
        sorted_words = sorted(self.words['words'].items(), key=lambda x: x[1], reverse=True)
        top_words = []
    
        # Get top words without stopwords
        for word in sorted_words:
            if word[0] not in self.stop_words:
                top_words.append(word)
            
            if len(top_words) == number:
                break
        
        #Display data
        print('\n-------TOP WORDS-------')
        for place, word in enumerate(top_words, 1):
            print(f'{place}. {word[0]} - {word[1]} times')
    
    def unique_words(self):
        print(f'There is {len(self.words["words"])} unique words')
    
    def unique_users(self):
        print(f'\nThere is {len(self.users)} unique users')
    
    def post_info(self):
        print(f'\nThere are {self.words["posts"]["number"]} posts and {self.words["posts"]["spoiler"]} are marked as spoilers')

    def comment_info(self):
        print(f'There are {self.words["comments"]["number"]} comments and {self.words["comments"]["spoiler"]} are marked as spoilers')
    
    def activity_info(self):
        activity = self.words['activity']

        print('\n-------ACTIVITY HOURS-------')
        for hour, value in activity.items():
            print(f'{hour} - {value} submissions')
        
        print(f'Sum of all sumbissions: {sum(activity.values())}')

    def create_summary(self, number_words, number_users):
        self.top_posters(number_users)
        self.top_submissions(number_users)
        self.top_commenters(number_users)
        self.unique_users()
        self.top_words(number_words)
        self.total_number_of_words()
        self.unique_words()
        self.post_info()
        self.comment_info()
        self.activity_info()


if __name__ == '__main__':
    with Summary('the100') as s :
        s.create_summary(10, 10)
        
    

