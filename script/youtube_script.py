import googleapiclient.discovery
import re
import time
import pandas as pd
import psycopg2
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from googleapiclient.errors import HttpError

# RDS Database Parameters
db_params = {
    'user': 'test:)',
    'password': 'test:)',
    'host': 'test:)',
    'port': 'test:)',
    'database': 'test:)'
}

# Remember that you need a youtube_key to put in googleapiclient.discovery.build
youtube_key = 'test:)'


def get_video_info_twice_japanese(video_id):
    """
    Get metadata information of a TWICE Japanese video from YouTube.

    Args:
        video_id (str): The unique identifier of the video.

    Returns:
        dict or None: A dictionary containing video metadata including title, views, likes, comments, published date,
                    artist, language, and retrieved date if successful. Returns None if video information is not found.
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
                cleaned_title = re.sub(r'TWICE|Music Video|「|」', '', title).strip().title()
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
                    'Artist': 'Twice', # Had problems fetching Artist Data, so it's hardcoded
                    'Language': 'Japanese'
                }
        except HttpError as e:
            print(f"An error occurred while fetching video information: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        if attempt < retries - 1:
            print(f"Trying again in 5 seconds...")
            time.sleep(5)
        else:
            print("Could not get video information after several attempts.")
            return None


def get_video_info_twice_korean(video_id):
#### Code
def get_video_info_twice_int(video_id):
#### Code
def get_video_info_itzy_japanese(video_id):
#### Code
def get_video_info_itzy_korean(video_id):
#### Code
def get_video_info_itzy_int(video_id):
#### Code
def get_video_info_nmixx_korean(video_id):
#### Code


def main():
    """
    Retrieves YouTube video data using specific video identifiers and different functions associated with
    various video types ('get_video_info_twice_japanese', 'get_video_info_twice_korean', etc.).
    It collects information using thread pooling and stores the gathered data in a CSV file.

    Note: Ensure that individual functions for each type of video are defined in the environment before
    executing this function.

    Returns:
    None
    """
    video_ids = {
        "get_video_info_twice_japanese": ["t35H2BVq490", "HuoOEry-Yc4", "wQ_POfToaVY", "r1CMjQ0QJ1E", "DdLYSziSXII",
                                        "X3H-4crGD6k", "CMNahhgR_ss", "3n9rDwpa6QA", "ZdKYi5ekshM", "zQELp93xxfo",
                                        "kRT174IdxuM", "sLmLwgxnPUE","BSS8Y-0hOlY", "fmOEKOjyDxU", "VcOSUOpACq0",
                                        "fMIn43MiwG8", "-uqWaGzQyxA"],
        "get_video_info_twice_korean": ["0rtV5esQT6I", "c7rCyll5AeY", "ePpPVE-GGJw", "8A2t_tAjMz8", "VQtonf1fv_s",
                                        "V2hlQkVJZhE", "rRzxEiBLQCA", "zi_6oaQyckM", "gfKPzQN_9ng", "i0p1bmr0EmE",
                                        "Fm5iP0S1z9w", "mAKsZ26SabQ", "CfUGjK6gGgs", "kOHB85vDuow", "3ymwOvzhwHs",
                                        "mH0_XpSHkZo", "CM4CkVFmTds", "XA2YEHn-A8Q", "vPwaXytZcgI", "k6jqx9kZgPM",
                                        "w4cTYnOPdNk"],
        "get_video_info_twice_int": ["f5_wn8mexmM", "cKlEE_EYuNM"],
        "get_video_info_itzy_japanese": ["yeHZNPplmm4", "ytTlH0EpSqI", "krzf1hkFAZA", "F-QTb-0wRGk", "K0xFPQ2CX5E",
                                        "5S1nsJs2O6s"],
        "get_video_info_itzy_korean": ["pNfTK39k55U", "zndvqTc4P9I", "fE2h3lGlOsk", "6rc_R5XvT3Q", "wTowEKjDGkU",
                                        "aASPZ-QdXMo", "hed6HkYNA7g", "_ysomCGaZLw", "WLQ7JqrCXec", "MjCZfZfucEc",
                                        "9oyodEkzn94", "OB7HVOCo6oQ", "Hbb5GPxXF1w", "zugAhfd2r0g", "RmTq3cJqyCo",
                                        "FcQ6oB1JPiA", "0bIRwBpBcZQ"],
        "get_video_info_itzy_int": ["tvTdg7sgsgU", "Ho_SmopuDlQ", "mCPkvzVLdHE", "6uZy86ePgO0"],
        "get_video_info_nmixx_korean": ["3GWscde8rM8", "oiSmwzPZOOo", "p1bjnyDqI9k", "4wKU9oIXnTI", "kBwikDvbRbI",
                                        "5eh6Vj_vVg4", "EDnwWcFpObo", "lH_n29wkT_4", "4q3JKyLc4xA", "fqBAzCH4-9g",
                                        "Rd2wppggYxo"]
    }

    data = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        for function_name, ids in video_ids.items():
            function = globals().get(function_name)
            if function is not None and callable(function):
                result = list(executor.map(function, ids))
                data.extend([video for video in result if video is not None])

    df = pd.DataFrame(data)
    df.columns = ['Video', 'Views', 'Likes', 'Comments', 'Published_Date', 'Retrieved_Date', 'Artist', 'Language']
    now = datetime.now().strftime("%Y%m%d")
    csv_file_name = f'data_{now}.csv'
    df.to_csv(csv_file_name, index=False)

    #print(df.head(2)) #This line is good to see if the script is executing well

    # RDS Connection
    conn = psycopg2.connect(**db_params)

    try:
        cur = conn.cursor()

        # Inserting data into the database from the DataFrame
        for row in df.itertuples(index=False):
            cur.execute(
                "INSERT INTO youtube_data.videos (video, views, likes, comments, published_date, retrieved_date, artist, language) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                (row.Video, row.Views, row.Likes, row.Comments, row.Published_Date, row.Retrieved_Date, row.Artist, row.Language)
            )

        # Confirm insertion
        conn.commit()
        print("Data inserted into database")

    except psycopg2.Error as e:
        conn.rollback()
        print("Error inserting data into database:", e)

    finally:
        conn.close()

if __name__ == "__main__":
    main()