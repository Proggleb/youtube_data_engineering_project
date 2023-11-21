import unittest
from youtube_get_metadata_script import clean_video_title

class TestCleanVideoTitle(unittest.TestCase):
    def test_clean_video_title(self):
        test_cases = [
            ("LE SSERAFIM 'Song Title' [OFFICIAL MV]", "Song Title"),
            ("LE SSERAFIM (르세라핌) 'Perfect Night' OFFICIAL M/V with OVERWATCH 2", "Perfect Night"),
        ]

        for dirty_title, expected_cleaned_title in test_cases:
            with self.subTest(dirty_title=dirty_title):
                cleaned_title = clean_video_title(dirty_title)
                self.assertEqual(cleaned_title, expected_cleaned_title)

if __name__ == '__main__':
    unittest.main()