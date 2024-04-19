# Not used. Because I don't have time to figure out how the Python import works.

import json
import bs4

def get_youtube_url_from_video_tag(tag: bs4.Tag) -> str:
    youtube_data_JSON:str = tag["data-setup"]
    yt_data_map:dict = json.loads(youtube_data_JSON)
    src:list = yt_data_map["sources"]
    src_0 = src[0]
    return src_0["src"]