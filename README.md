# SubInfo
It is a script for gathering some information about reddit subreddits.

## Instalation
Currently the only way to install my script is downloading it from github, I will add executable file soon.

#### Requirements
- Python 3.5 or higher

## Usage
To run the script you have to pass this obligatory argument:
- `-n`/`--name` - Name of a subreddit
You can also add optional arguments:
- `-s`/`--summary` - If you wnat to display summary of the subreddit info in terminal
- `-f`/`--file` - If you want to get data from file instead of downloading it
- `-d`/`--database` - If you want to save data to sql database. **You have to pass name for a database after this flag(without extensions)**
- `-u`/`--users` - Number of top users that you want to display in summary
- `-w`/`--words` - Number of top words that you want to display in summary

## Data that script will gather
- Number of posts and comments for every user that has submited at least once to a subreddit
- Count of every word in posts and comments in a subreddit
- Count of posts and comments
- How many times spoiler tag was used
- How many submissions there is for each hour

## What does summary shows
- Top posters
- Top commentors
- Top submission users
- Top used words
- Number of all used words
- Number of unique words
- Activity hours of a subreddit
- Sum of all submissions

## How data is structured in json files
#### users_SubredditName.json
    {
        USERNAME: {'posts': COUNT, 'comments': COUNT}
    }

#### words_SubredditName.json
    {
        'words': {WORD: COUNT}
        'posts': {'number': COUNT, 'spoiler': COUNT}
        'comments': {'number': COUNT, 'spoiler': COUNT}
        'activity': {'0': COUNT, '1': COUNT, ... , '22': COUNT, '23': COUNT}
    }

## How data is structured in SQL database
- Table `words`
    - WORD : COUNT 
- Table `users`
    - USER : POST : COUNT
- Table `submissions`
    - TYPE : COUNT : SPOILER_COUNT
- Table `sub_times`
    - HOUR : COUNT

## Stop words
You have a list of stop words inside `stopwords.txt` that will be excluded from summary. Example of sucha a word is 'was', 'you', 'however' etc. You can add your own stop words by appending the txt file. **NOTE: Every word has to be in different line** 

## Example usage
Running the script is pretty simple, all you need is a subreddit name. You can find exact name inside subreddit url, we will use `learnpython` subreddit.
This is out subreddit url: `https://www.reddit.com/r/learnpython/`. You can see the exact name after `/r/` and it is `learnpython`.

All you have to do is run `python subInfo.py -n learnpython -s` and downloading process will start. Dates my confuse you at first, but data is being downloaded in chunkes(500 submissions) and this means that this is a date of last downloaded submission and script is downloading next 500 since then.
[example](https://github.com/kubapilch/SubInfo/blob/master/examples/subInf.JPG)

**It can take several dozen of minutes depending on your disc speed, internet connection and size of a subreddit.**