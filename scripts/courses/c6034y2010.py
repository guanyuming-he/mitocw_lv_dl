import pathlib
import bs4
import json

from . import helpers
from . import course


class c6034_gallery(course.video_gallery_course):

    def __init__(
        self, res_path: pathlib.Path, downloader_type: str,
    ):
        """
        Parameters
        ----------
        res_path: Path
            a path to the static resources of the course.

        downloader_type: str
            the type of the downloader. 
            This type of courses store youtube urls in their video_galleries.
            Therefore, str cannot be "300k"

        """
        super().__init__(
            res_path, downloader_type,
            {
                "Lecture"           : "lecture-videos",
                "Mega-Recitation"   : "mega-recitation-videos"
            }
        )


my_info = course.course_info([course.three_100k_course, c6034_gallery])


"""
def populate_video_maps_list(static_root_path: pathlib.Path, verbose:bool = False) -> dict:

    if(not static_root_path.exists() or not static_root_path.is_dir()):
        raise ValueError("static_root_path does not exist or is not a directory.")
    
    # Find lectures from the index.html.
    res_dir_path = static_root_path / "video_galleries"

    #################### Lecture Videos ############################
    lec_ind_html_path = res_dir_path / "lecture-videos" / "index.html"
    lec_ind_bs:bs4.BeautifulSoup = helpers.give_me_bs(lec_ind_html_path)

    # Get the html pages of the lecture videos.
    list_lec_html_paths:list = helpers.grab_html_from_galleries_index_html(
        lec_ind_bs, lec_ind_html_path.parent, verbose
    )
    list_lec_vids:list = []

    # turn each html page into a map of title -> url
    for hp in list_lec_html_paths:
        bs = helpers.give_me_bs(hp)
        tit_url_map = helpers.grab_title_url_from_youtube_html_page(
            bs, "Lecture", verbose
        )
        list_lec_vids.append(tit_url_map)

    # Add lecture numbers to the list
    list_lec_vids = [
        (i+1, list_lec_vids[i]) for i in range(len(list_lec_vids))
    ]

    #################### Recitation Videos ############################
    rec_ind_html_path = res_dir_path / "mega-recitation-videos" / "index.html"
    rec_ind_bs:bs4.BeautifulSoup = helpers.give_me_bs(rec_ind_html_path)

    # Get the html pages of the recitation videos.
    list_rec_html_paths:list = helpers.grab_html_from_galleries_index_html(
        rec_ind_bs, rec_ind_html_path.parent, verbose
    )
    list_rec_vids:list = []

    # turn each html page into a map of title -> url
    for hp in list_rec_html_paths:
        bs = helpers.give_me_bs(hp)
        tit_url_map = helpers.grab_title_url_from_youtube_html_page(
            bs, "Mega-Recitation", verbose
        )
        list_rec_vids.append(tit_url_map)

    # Add recitation numbers to the list
    list_rec_vids = [
        (i+1, list_rec_vids[i]) for i in range(len(list_rec_vids))
    ]

    ret:dict = {}
    ret["Lecture"] = list_lec_vids
    ret["Mega-Recitation"] = list_rec_vids
    return ret


def youtube_available() -> bool:
    return True
"""
