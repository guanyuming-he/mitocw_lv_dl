import pathlib
import bs4
import json

def populate_video_maps_list(static_root_path: pathlib.Path, verbose:bool = False) -> list:

    if(not static_root_path.exists() or not static_root_path.is_dir()):
        raise ValueError("static_root_path does not exist or is not a directory.")
    
    NUM_LECTURERS = 21

    # 1. to fill the video_maps_list, first I must find all video .html file for each lecture.
    # lecture index -> list of .html file paths
    video_html_file_path_list = []
    
    i0 = 0
    for i0 in range(NUM_LECTURERS):
        # lecture index = i
        # path is root/pages/ci/cis2
        # each video is contained inside path/cis2vj as index.html,
        # where j is the video index
        i = i0+1
        lecture_videos_path : pathlib.Path = static_root_path / "pages"
        lecture_videos_path /= ('c' + str(i) + '/' + 'c' + str(i) + "s2")
        video_dirs = [
            dir 
            for dir in lecture_videos_path.iterdir() 
            if dir.is_dir()
        ]
        temp = []
        for dir in video_dirs:
            v_path = pathlib.Path(dir) / "index.html"
            assert (v_path.exists())
            temp.append(v_path)
        video_html_file_path_list.append(temp)

    # 2. from each .html file find the video title and URL
    video_maps_list:list = list()

    i0 = 0
    for i0 in range(NUM_LECTURERS):
        i = i0+1

        videos_map = {}

        html_paths:list = video_html_file_path_list[i0]
        for html_path in html_paths:
            html = open(html_path, 'r')
            bs:bs4.BeautifulSoup = bs4.BeautifulSoup(html, "html.parser")

            course_content_section:bs4.Tag = bs.find("main", id="course-content-section")
            assert(course_content_section is not None)
            title_tag:bs4.Tag = course_content_section.find("h3")
            assert(title_tag.has_attr("id"))
            video_title:str = title_tag.contents[0]
            # the current video title is in the format:
            # name (MM:ss)
            # but a file name cannot have : on some OS.
            # Therefore, remove (MM:ss) from it
            lp_ind = video_title.find(' (')
            if(lp_ind != -1):
                video_title = video_title[:lp_ind]
            # To index them, add the video index to the title.
            # The index is available in the html path
            html_path_parent:pathlib.Path = pathlib.Path(html_path).parent
            video_title = html_path_parent.name + ", " + video_title

            youtube_video_tag:bs4.Tag = course_content_section.find("video")
            assert(youtube_video_tag is not None)

            # the youtube video source data is stored in JSON
            youtube_data_JSON:str = youtube_video_tag["data-setup"]
            yt_data_map:dict = json.loads(youtube_data_JSON)
            src:list = yt_data_map["sources"]
            src_0 = src[0]
            youtube_URL:str = src_0["src"]

            videos_map[video_title] = youtube_URL

        video_maps_list.append(videos_map)

    if(verbose):
        print("video_maps_list=")
        print(video_maps_list)

    return video_maps_list

def youtube_available() -> bool:
    return True