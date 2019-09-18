from downloading import SubredditStatistics
from summary import Summary
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--name', help='Name of a subreddit', required=True)
    parser.add_argument('-f', '--file', help='If you want to get summary from previously downloaded and saved data', default=False, action='store_true')
    parser.add_argument('-d', '--database', help='Database name if you want to save to sql database insead of json files')
    
    # Parse arguments
    print('Parsing arguments..')
    args = parser.parse_args()

    subreddit_name = args.name

    if not args.file :
        if args.database:
            with SubredditStatistics(subreddit_name, database_name=args.database, database=True) as s:
                s.download_and_save_statistics()
        else:
            with SubredditStatistics(subreddit_name) as s:
                s.download_and_save_statistics()

    print('-------DATA HAS BEEN DOWNLOADED-------')


if __name__=='__main__':
    parse_arguments()