import bs4
import json

def give_me_bs(path_to_html)-> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(open(
        path_to_html, 'r'), "html.parser"
    )

def grab_title_url_from_300k_resources_index_html(
        res_bs:bs4.BeautifulSoup,
        video_type:str,
        verbose:bool
    )-> list:
    """
    Given a html file of a index.html that stores 300k
    videos and their titles as
    "resource-thumbnail" sections and
    "resource-list-title" sections, respectively,

    this function grabs them and form a list of maps.

        Parameters:
            res_bs: bs4 object of the html page
            video_type: Describes the videos. (e.g. Lecture, Recitation)
            verbose: verbose.

        Returns:
            A list of maps.
            Each map corresponds to a video session (e.g. Lecture 1, Recitation 2)
            It maps each title of a video to its URL.
            NOTE: I do not give the video numbers accompanying the maps.
            This is because some numbers are contained in the titles 
            while some are not and can only be inferred from the indexing of the list.
    """
    ret:list = []

    # Course URL section and title section are contained in such containers
    course_containers = res_bs.find_all("div", class_="d-inline-flex")

    for c in course_containers:
        # maps title to URL for this course session
        videos_map = {}

        title_section = c.find('a', class_="resource-list-title")
        video_section = c.find('a', class_="resource-thumbnail")
        assert title_section is not None and video_section is not None
        if verbose:
            print(f"title_section is {title_section}")
            print(f"video_section is {video_section}")

        # Get the video title.
        video_title:str = title_section.get_text()

        url = video_section["href"]
        # I only want English videos here.
        if "zh-hans" in url:
            continue

        videos_map[video_title] = url

        if verbose:
            print(f"{video_type} found: {video_title}: {url}")
        ret.append(videos_map)

    return ret


def grab_title_url_from_youtube_html_page(
        bs:bs4.BeautifulSoup,
        video_type:str,
        verbose:bool
):
    """
    Takes in a html page of a SINGLE youtube video,
    returns a map of title -> url
    """
    title_section = bs.select("div.course-section-title-container")[0]
    video_section = bs.find("video")
    assert title_section is not None and video_section is not None
    if verbose:
        print(f"title_section is {title_section}")
        print(f"video_section is {video_section}")

    # Get the video title and video number
    video_title:str = title_section.find("h2").get_text()

    # the youtube video source data is stored in JSON
    youtube_data_JSON:str = video_section["data-setup"]
    yt_data_map:dict = json.loads(youtube_data_JSON)
    src:list = yt_data_map["sources"]
    src_0 = src[0]
    youtube_URL:str = src_0["src"]

    if verbose:
        print(f"{video_type} found: {youtube_URL}")
    return {video_title: youtube_URL}

