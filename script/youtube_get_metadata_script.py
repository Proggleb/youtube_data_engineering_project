import os
import googleapiclient.discovery
import re
import time
import pandas as pd
import psycopg2
from functools import wraps
from contextlib import contextmanager
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from googleapiclient.errors import HttpError

# RDS Parameters
db_params = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
    'database': os.environ.get('DB_DATABASE')
}

# Youtube API Key
youtube_key = os.environ.get('YOUTUBE_API_KEY')

# Videos Dictionary
## ADD Video_ids from youtube videos to get their metadata.
video_ids = {
    "get_video_info": ["4vbDFu0PUew", "pyf8cbqyfPs, Ccz123Jlflc", "UBURTj20HXI", "dZs_cLHfnNA",
                    "DiGnWwgLAfE", "vMddOrUGwDw", "hLvWy2b857I"]
}

# Insertion Query
## You can modify your query
schema_name='SCHEMA_NAME'
table_name='TABLE_NAME'

INSERT_QUERY = f"""
    INSERT INTO {schema_name}.{table_name}
    (video, views, likes, comments, published_date, retrieved_date, artist)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
"""


@contextmanager
def db_connection(db_params):
    """
    A context manager decorator for handling the connection and closure of a database.

    Parameters:
    - db_params (dict): A dictionary containing the parameters needed to establish a database connection,
                    including 'user', 'password', 'host', 'port', and 'database'.

    Yields:
    - connection (psycopg2.extensions.connection): A database connection object.
    """
    connection = psycopg2.connect(**db_params)
    try:
        yield connection
    finally:
        connection.close()


def db_cursor(func):
    """
    Decorator for managing the database cursor.
    This decorator ensures the proper handling of the database cursor within a function.

    Parameters:
    - func (callable): The function to be decorated.

    Returns:
    - wrapper (callable): The decorated function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = kwargs.get('conn') or args[0]
        with conn.cursor() as cursor:
            kwargs['cursor'] = cursor
            result = func(*args, **kwargs)
        return result
    return wrapper


def insert_into_database(row, conn):
    """
    Function to store data in the database.
    This function inserts a row of data into the specified database table.

    Parameters:
    - row (pandas.Series): A pandas Series representing a row of data to be inserted.
    - conn (psycopg2.extensions.connection): The database connection object.

    Raises:
    - psycopg2.Error: If an error occurs during the database operation.

    Returns:
    - None
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                INSERT_QUERY,
                (row.Video, row.Views, row.Likes, row.Comments, row.Published_Date, row.Retrieved_Date, row.Artist)
            )

        # Confirm the insertion
        conn.commit()
        # print("Data inserted into the database")          # You can change to LOGGING
    except psycopg2.Error as e:
        conn.rollback()
        # Print which video caused the exception
        print(f"Error inserting data into the database for video: {row.Video}")
        print("Error details:", e)


def execute_threads(video_ids):
    """
    Function to execute threads and gather results into a list.
    This function utilizes a ThreadPoolExecutor to concurrently execute functions for multiple video IDs.

    Parameters:
    - video_ids (dict): A dictionary where keys are function names and values are lists of video IDs.

    Returns:
    - data (list): A list containing the results from the executed threads.
    """
    data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for function_name, ids in video_ids.items():
            function = globals().get(function_name)
            if function is not None and callable(function):
                result = list(executor.map(function, ids))
                data.extend([video for video in result if video is not None])
    return data


def create_dataframe(data):
    """
    Function to create a DataFrame from a list of results.
    This function takes a list of results and converts it into a Pandas DataFrame.

    Parameters:
    - data (list): A list containing results to be converted into a DataFrame.

    Returns:
    - df (pandas.DataFrame): A DataFrame containing the specified columns.
    """
    df = pd.DataFrame(data)
    df.columns = ['Video', 'Views', 'Likes', 'Comments', 'Published_Date', 'Retrieved_Date', 'Artist']
    return df


def write_to_csv(df):
    """
    Function to write data to a CSV file.
    This function takes a Pandas DataFrame and writes its contents to a CSV file.
    The CSV file is named based on the current date.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing data to be written to the CSV file.

    Returns:
    - None
    """
    now = datetime.now().strftime("%Y%m%d")
    csv_file_name = f'lesserafim_{now}.csv'
    df.to_csv(csv_file_name, index=False)
    print(f"Data written to {csv_file_name}")


def clean_video_title(title):
    """
    Function to clean video titles.
    This function applies a regular expression pattern to remove specific phrases and symbols
    commonly found in video titles. The cleaned title is then formatted to title case.

    Parameters:
    - title (str): The original video title.

    Returns:
    - clean_title (str): The cleaned and formatted video title.
    """
    # Regular expression pattern to extract the song title
    pattern = re.compile(r"\(.*?\)|\[.*?\]|OFFICIAL M/V|OFFICIAL MV|LE SSERAFIM|'|‘|’", flags=re.IGNORECASE)
    clean_title = re.sub(pattern, "", title).strip().title()
    return clean_title


def get_video_info(video_id):
    """
    Function to extract metadata for YouTube videos.
    This function uses the YouTube API to retrieve metadata, including title, views, likes, comments,
    publication date, and retrieval date for a given video ID.

    Parameters:
    - video_id (str): The unique identifier of the YouTube video.

    Returns:
    - video_data (dict): A dictionary containing the extracted metadata.

    Note:
    - The 'Artist' field is hardcoded to 'Le Sserafim' due to difficulties fetching artist data.
    - HTTP errors and unexpected errors are handled with retries.
    - The 'Retrieved Date' is set to the current date.
    """
    retries = 3
    for attempt in range(retries):
        try:
            api_service_name = "youtube"
            api_version = "v3"

            youtube = googleapiclient.discovery.build(api_service_name,
                                                    api_version,
                                                    developerKey=youtube_key)

            request = youtube.videos().list(part="snippet, statistics",
                                            id=video_id)
            response = request.execute()

            if 'items' in response and response['items']:
                video_info = response['items'][0]
                snippet = video_info['snippet']
                title = snippet['title']
                # Clean the title using the 'clean_video_title' function
                cleaned_title = clean_video_title(title)
                views = video_info['statistics']['viewCount']
                try:
                    likes = int(video_info['statistics'].get('likeCount', 0))
                except (KeyError, ValueError):
                    likes = 0
                comments = video_info['statistics']['commentCount']
                published_at = snippet['publishedAt']
                published_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ").date()
                retrieved_date = datetime.now().date()

                return {
                    'Video': cleaned_title,
                    'Views': views,
                    'Likes': likes,
                    'Comments': comments,
                    'Published Date': published_date,
                    'Retrieved Date': retrieved_date,
                    'Artist': 'Le Sserafim',
                }
        except HttpError as e:
            print(f"Error: An HTTP error occurred while fetching video information: {e}")
            return None
        except Exception as e:
            print(f"Error: An unexpected error occurred while fetching video information: {e}")
            return None
        if attempt < retries - 1:
            print(f"Retrying in 5 seconds...")
            time.sleep(5)
        else:
            print("Error: Could not get video information after several attempts.")
            return None


@db_connection(db_params)
def main(conn):
    """
    Main function using the connection decorator.
    This function demonstrates the use of the 'db_connection' decorator to manage the database connection.
    It executes threads to gather data, creates a DataFrame, writes data to a CSV file, and inserts data into the database.

    Parameters:
    - conn (psycopg2.extensions.connection): The database connection object.

    Returns:
    - None
    """
    data = execute_threads(video_ids)

    df = create_dataframe(data)

    write_to_csv(df)

    for row in df.itertuples(index=False):
        insert_into_database(row, conn)

if __name__ == "__main__":
    with db_connection(db_params) as conn:
        main(conn)