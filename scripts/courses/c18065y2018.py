import pathlib
import bs4
import json

def populate_video_maps_list(static_root_path: pathlib.Path, verbose:bool = False) -> list:

    if(not static_root_path.exists() or not static_root_path.is_dir()):
        raise ValueError("static_root_path does not exist or is not a directory.")
    
    # 1. to fill the video_maps_list, first I must find all video .html file for each lecture.
    video_html_file_path_list:list = []

    # Find lectures from the filesystem.
    res_dir_path = static_root_path / "resources"
    lecture_dirs = [d for d in res_dir_path.iterdir() 
                    if d.is_dir() and d.name.startswith('lecture-') and d.name[8].isnumeric()]

    for ld in lecture_dirs:
        # Now each c is the course video's html path relative to the index pages.
        lecture_video_path : pathlib.Path = ld / "index.html"
        video_html_file_path_list.append(lecture_video_path)

    # 2. from each .html file find the video title and URL
    video_maps_list:list = list()

    for i in range(len(video_html_file_path_list)):
        videos_map = {}

        html_path = video_html_file_path_list[i]
        bs:bs4.BeautifulSoup = bs4.BeautifulSoup(open(
            html_path, 'r'), "html.parser"
        )

        title_section = bs.select("div.course-section-title-container")[0]
        video_section = bs.find("video")
        assert title_section is not None and video_section is not None
        if verbose:
            print(f"title_section is {title_section}")
            print(f"video_section is {video_section}")

        # Get the video title and video number
        video_title:str = title_section.find("h2").get_text()
        assert video_title[:8] == "Lecture "
        li = video_title[8]
        # The course number may have several digits
        for i in range(9, len(video_title)):
            if video_title[i].isnumeric():
                li = li + video_title[i]
        # the video number
        li = int(li)

        # the youtube video source data is stored in JSON
        youtube_data_JSON:str = video_section["data-setup"]
        yt_data_map:dict = json.loads(youtube_data_JSON)
        src:list = yt_data_map["sources"]
        src_0 = src[0]
        youtube_URL:str = src_0["src"]

        videos_map[video_title] = youtube_URL

        tp = (li, videos_map)
        if verbose:
            print(f"Lecture found: {tp}")
        video_maps_list.append((li, videos_map))

    if(verbose):
        print("video_maps_list=")
        print(video_maps_list)

    # Recitations are to be added.
    ret:map = {}
    ret["Lecture"] = video_maps_list
    return ret

def youtube_available() -> bool:
    return True
