import pathlib
import bs4
import json
from . import helpers

def populate_video_maps_list(static_root_path: pathlib.Path, verbose:bool = False) -> list:

    if(not static_root_path.exists() or not static_root_path.is_dir()):
        raise ValueError("static_root_path does not exist or is not a directory.")
    
    # Find lectures from the index.html.
    res_dir_path = static_root_path / "resources"

    #################### Lecture Videos ############################
    lec_ind_html_path = res_dir_path / "lecture-videos" / "index.html"
    lec_ind_bs:bs4.BeautifulSoup = helpers.give_me_bs(lec_ind_html_path)

    list_lec_vids = helpers.grab_title_url_from_300k_resources_index_html(
        lec_ind_bs, "Lecture", verbose
    )
    # Add lecture numbers to the list
    list_lec_vids = [
        (i+1, list_lec_vids[i]) for i in range(len(list_lec_vids))
    ]

    #################### Recitation Videos ############################
    rec_ind_html_path = res_dir_path / "recitation-videos" / "index.html"
    rec_ind_bs:bs4.BeautifulSoup = helpers.give_me_bs(rec_ind_html_path)

    list_rec_vids = helpers.grab_title_url_from_300k_resources_index_html(
        rec_ind_bs, "Recitation", verbose
    )
    # Add recitation numbers to the list
    list_rec_vids = [
        (i+1, list_rec_vids[i]) for i in range(len(list_rec_vids))
    ]

    ret:map = {}
    ret["Lecture"] = list_lec_vids
    ret["Recitation"] = list_rec_vids
    return ret

def youtube_available() -> bool:
    # For this course, we don't use YouTube URLs, as they are also either 360p or 480p
    return False
