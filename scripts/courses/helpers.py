import bs4
import json
import pathlib
import requests

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


def grab_html_from_resources_index_html(
        res_bs:bs4.BeautifulSoup,
        base_path,
        verbose:bool
    )-> list:
    """
    Given a html file of a index.html from resources/ that stores 
    a list of videos,

    this function grabs the html file paths to these video pages.

        Parameters:
            res_bs: bs4 object of the html page
            base_path: the path that the html paths are relative to
            verbose: verbose.

        Returns:
            A list of html paths to the videos.
The paths will be processed to become absolute.
    """
    ret:list = []

    # Course URL section and title section are contained in such containers
    course_containers = res_bs.find_all("div", class_="d-inline-flex")

    for c in course_containers:
        html_section = c.find('a', class_="resource-list-title")
        assert html_section is not None
        relative_path = html_section["href"]

        if verbose:
            print(f"page found: {relative_path}") 
        ret.append(base_path / relative_path)

    return ret


def grab_html_from_galleries_index_html(
        res_bs:bs4.BeautifulSoup,
        base_path,
        verbose:bool
    )-> list:
    """
    Given a html file of a index.html from video_galleries/ that stores 
    a list of videos,

    this function grabs the html file paths to these video pages.

        Parameters:
            res_bs: bs4 object of the html page
            base_path: the path that the html paths are relative to
            verbose: verbose.

        Returns:
            A list of html paths to the videos.
            The paths will be processed to become absolute.
    """
    ret:list = []

    # Course URL section and title section are contained in such containers
    course_containers = res_bs.find_all("a", class_="video-link")

    for c in course_containers:
        relative_path = c["href"]

        if verbose:
            print(f"page found: {relative_path}") 
        ret.append(base_path / relative_path)

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


def download_file_over_http(
    url: str,
    file_path: pathlib.Path,
    chunk_size: int = 16*1024,
    num_retries: int = 8,
    verbose: bool = False
) -> bool:
    """
    Downloads a file over HTTP from url,
    to the file pointed to by file_path.

    Parameters
    ----------
    url : str
        HTTP url to the file.
    file_path : Path
        path to an entry to a directory in the file system.
        The entry may or may not exist, but the directory
        that contains it must exist.
    chunk_size : int, optional
        size of the chunk that is transfered at once
        over the network.
    num_retries : int, optional
        number of retries before a final failure.
    verbose : bool, optional
        Will print the retries iff True.

    Returns
    -------
    bool
        True iff the downloading was successful.
    """
    for i in range(num_retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Check for HTTP errors

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(
                    chunk_size=chunk_size
                ):
                    file.write(chunk)
            
            # Success
            return True

        except Exception as e:
            if verbose:
                print(f"An error occurred while downloading from {url}:")
                print(e)
                print(f"Retry number {i+1}.")
            continue

    # all retries have failed
    return False

