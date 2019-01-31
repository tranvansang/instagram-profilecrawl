import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings:
    profile_location = os.path.join(BASE_DIR, 'profiles')
    profile_commentors_location = os.path.join(BASE_DIR, 'profiles')
    profile_file_with_timestamp = False
    profile_commentors_file_with_timestamp = False
    limit_amount = 12
    scrap_posts_infos = True
    output_comments = False
    sleep_time_between_post_scroll = 1.5
    mentions = True
