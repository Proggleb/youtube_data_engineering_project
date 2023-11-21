import os
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from youtube_get_metadata_script import get_video_info

youtube_key = os.environ.get('YOUTUBE_API_KEY')

class TestGetVideoInfo(unittest.TestCase):

    @patch('lesserafim.googleapiclient.discovery.build')
    def test_get_video_info(self, mock_youtube_build):
        # Simulate answer from Youtube API
        mock_execute = MagicMock()
        mock_execute.return_value = {
            'items': [{
                'snippet': {
                    'title': 'Test Video',
                    'publishedAt': '2023-01-01T12:00:00Z',
                },
                'statistics': {
                    'viewCount': 100,
                    'likeCount': 10,
                    'commentCount': 5,
                }
            }]
        }
        mock_youtube_build.return_value.videos.return_value.list.return_value.execute = mock_execute

        # Call function to Test
        video_data = get_video_info('test_video_id')

        # Define expected dates
        expected_published_date = datetime.strptime('2023-01-01', "%Y-%m-%d").date()
        expected_retrieved_date = datetime.now().date()

        # Verifies Function return the expected result
        self.assertEqual(video_data, {
            'Video': 'Test Video',
            'Views': 100,
            'Likes': 10,
            'Comments': 5,
            'Published Date': expected_published_date,
            'Retrieved Date': expected_retrieved_date,
            'Artist': 'Le Sserafim',
        })

        # Verifies Function did Call Youtube API
        mock_youtube_build.assert_called_once_with("youtube", "v3", developerKey=youtube_key)
        mock_youtube_build.return_value.videos.return_value.list.assert_called_once_with(
            part="snippet, statistics",
            id='test_video_id'
        )
        mock_execute.assert_called_once()

if __name__ == '__main__':
    unittest.main()