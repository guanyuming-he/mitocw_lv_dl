import pathlib
import bs4
import json

def get_youtube_url_from_video_tag(tag: bs4.Tag) -> str:
    youtube_data_JSON:str = tag["data-setup"]
    yt_data_map:dict = json.loads(youtube_data_JSON)
    src:list = yt_data_map["sources"]
    src_0 = src[0]
    return src_0["src"]

def populate_video_maps_list(static_root_path: pathlib.Path, verbose:bool = False) -> list:

    if(not static_root_path.exists() or not static_root_path.is_dir()):
        raise ValueError("static_root_path does not exist or is not a directory.")
    
    # 1. to fill the video_maps_list, first I must find all video .html file for each lecture.
    # In this course, the title of a video is also available where the .html file path is stored.
    # This list:
    # lecture index -> {title |-> html path}
    video_title_html_path_maps_list = []

    lv_ind_html_path = static_root_path / "resources" / "lecture-videos" / "index.html";
    assert(lv_ind_html_path.exists() and lv_ind_html_path.is_file())

    lv_ind_html = open(lv_ind_html_path)
    lv_ind_bs = bs4.BeautifulSoup(lv_ind_html, "html.parser")
    
    video_a_container_divs:list = lv_ind_bs.find_all("div", attrs={"class": "resource-list-item-details"})

    lv_ind_list_item:bs4.Tag
    # Need to track the last session number to see if an iteration enters a new session.
    last_session_num:int = 1
    temp_title_html_path_map: dict = dict()
    for lv_ind_list_item in video_a_container_divs:
        # This a tag contains the video html page.
        list_item_details_a:bs4.Tag = lv_ind_list_item.find("a")
        assert(list_item_details_a is not None)

        # The title is the content of the details_div
        title:str = list_item_details_a.get_text()
        # remove illegal characters for filename
        title = title.replace('\n', '')
        # the title is in this format " Session i ..."
        # Therefore, the session number can be obtained from it.
        session_str_ind:int = title.find("Session")
        clip_str_ind:int = title.find("Clip")
        session_num_title:int = int(title[session_str_ind+8:clip_str_ind-1])

        # The path contained in href attribute is relative to lv_ind_html_path
        relative_path:str = list_item_details_a["href"]
        html_path: pathlib.Path = lv_ind_html_path.parent / relative_path

        # Check we have entered a new session. If so, start a new map to mark a new lecture.
        if (session_num_title > last_session_num):
            last_session_num = session_num_title
            video_title_html_path_maps_list.append(temp_title_html_path_map)
            temp_title_html_path_map = dict()

        # Add this title and path pair to the map
        temp_title_html_path_map[title] = html_path

    # After the loop, don't forget to append the map one more time
    video_title_html_path_maps_list.append(temp_title_html_path_map)

    # 2. replace each html path with the youtube url
    # After this, video_title_html_path_maps_list becomes the return value
    for map in video_title_html_path_maps_list:
        for (title, html_path) in map.items():
            bs:bs4.BeautifulSoup = bs4.BeautifulSoup(open(html_path), "html.parser")
            video_tag:bs4.Tag = bs.find("video")

            # the youtube video source data is stored in JSON
            map[title] = get_youtube_url_from_video_tag(video_tag)

    # 3 verbose output
    if (verbose):
        print(video_title_html_path_maps_list)

    return video_title_html_path_maps_list
 
def youtube_available() -> bool:
    return True

# For debugging, execute this script under the parent of static
populate_video_maps_list(pathlib.Path("./static"), True)