import pathlib
import bs4
import re

from . import helpers
from . import course

class c18065_gallery(course.video_gallery_course):

    def __init__(self, res_path: pathlib.Path, downloader_type: str):
        super().__init__(
            res_path, downloader_type,
            { "Lecture" : "video-lectures" }
        )

my_info = course.course_info([course.three_100k_course, c18065_gallery])


"""
LEC_RE_OBJ = re.compile(r"Lecture ([\d]+)")
REC_RE_OBJ = re.compile(r"Recitation ([\d]+)")

def populate_video_maps_list(static_root_path: pathlib.Path, verbose:bool = False) -> list:

    if(not static_root_path.exists() or not static_root_path.is_dir()):
        raise ValueError("static_root_path does not exist or is not a directory.")
    
    ################# Lectures #################
    # 1. to fill the lec_maps_list, first I must find all video .html file for each lecture.
    lec_html_file_path_list:list = []

    # Find lectures from the filesystem.
    res_dir_path = static_root_path / "resources"
    lecture_dirs = [d for d in res_dir_path.iterdir() 
                    if d.is_dir() and d.name.startswith('lecture-') and d.name[8].isnumeric()]

    for ld in lecture_dirs:
        # Now each c is the course video's html path relative to the index pages.
        lecture_lec_path : pathlib.Path = ld / "index.html"
        lec_html_file_path_list.append(lecture_lec_path)

    # 2. from each .html file find the video title and URL
    lec_maps_list:list = list()

    for i in range(len(lec_html_file_path_list)):
        videos_map = {}

        html_path = lec_html_file_path_list[i]
        bs:bs4.BeautifulSoup = bs4.BeautifulSoup(open(
            html_path, 'r'), "html.parser"
        )

        tit_url_map = helpers.grab_title_url_from_youtube_html_page(
            bs, "Lecture", verbose
        )
        title = next(iter(tit_url_map))
        # Find the lecture number from the titles
        num_l:int = -1
        match = LEC_RE_OBJ.match(title)
        if match:
            num_l = int(match.group(1))
        else:
            raise ValueError("lecture number not found")
        
        lec_maps_list.append((num_l, tit_url_map))

    if(verbose):
        print("Lectures=")
        print(lec_maps_list)

    ret:map = {}
    ret["Lecture"] = lec_maps_list
    return ret

def youtube_available() -> bool:
    return True
"""
