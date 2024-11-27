import video_downloader
import pathlib

# In case the script is run on Windows, I will replace every illegal character in NTFS with #
ILLEGAL_NTFS_CHARS = "\\/:*?\"<>|"
ILLEGAL_CHAR_TRANS_TABLE = str.maketrans({char: '#' for char in ILLEGAL_NTFS_CHARS})

def start_download(
    video_maps: dict, 
    videos_root: pathlib.Path, 
    downloader: video_downloader.video_downloader,
    verbose:bool = False
) -> None:
    """
    Download all videos in video_maps into videos_root,
    creating a subdirectory for each lecture/reitation/etc.
    The downloading will be done using downloader.

        Parameters:
            video_maps (map): map of lists of tuples. 
                Each key is the name of type of videos (e.g. "Lecture", "Recitation")
                Each key is mapped to a list of tuples (num, url_map).
                where num is the video number,
                and url_map is a map that maps titles to video urls. 
                Each map is arranged in the order that the videos are given.
            videos_root (pathlib.Path):
                path to the directory where all the videos downloaded 
                are to be placed in.
            downloader:
                The ADT that handles the downloading.

        Requires:
            The maps is not empty; the video urls are valid.
            The videos_root exists.
            downloader is valid.

        Ensures:
            Exactly as said in the description.
            The videos will be created with the corresponding keys in the maps
            as their filename, with illegal characters in NTFS replaced by #,
            in case the scripts are executed on Windows.
            Will only output extra information if verbose=True
    """
    if len(video_maps) == 0:
        raise ValueError("The list of video maps is empty.")
    if not videos_root.exists() or not videos_root.is_dir():
        raise ValueError("The root for videos downloaded does not exist or is not a directory.")
    if downloader is None:
        raise ValueError("The downloader is none.")
    
    # Type of the video, e.g. "Lecture", "Recitation".
    video_type:str
    for video_type in video_maps:
        # Add 's' to mean plural form.
        video_type_dir = videos_root / (video_type + 's')

        # list of video maps for the video_type.
        list_video_maps: list = video_maps[video_type]
        video_type_dir.mkdir(exist_ok=True)

        for (vid_num, video_map) in list_video_maps:

            str_vn:str = str(vid_num)
            if (verbose):
                print(f"downloading videos for {video_type} {str_vn}")

            # Videos for a session will be placed under root/video_type/number/
            video_dir: pathlib.Path = video_type_dir / str_vn
            if(not video_dir.exists() or not video_dir.is_dir()):
                video_dir.mkdir(exist_ok=True)

            downloader.chdir(video_dir)

            title:str
            for (title, url) in video_map.items():
                # Replace illegal filename characters with #
                title = title.translate(ILLEGAL_CHAR_TRANS_TABLE)
                downloader.download(title, url, verbose)

# Import courses
import courses.c6004y2017
import courses.c18065y2018
import courses.c1806scy2011
import courses.c6034y2010
import courses.c6858y2014
import courses.fmsd_hehner

# Maps <course-number>-<year> to the course's my_info
COURSE_MAP:dict = dict()
COURSE_MAP["6.004-2017"] = courses.c6004y2017.my_info
COURSE_MAP["18.065-2018"] = courses.c18065y2018.my_info
COURSE_MAP["18.06sc-2011"] = courses.c1806scy2011.my_info
COURSE_MAP["6.034-2010"] = courses.c6034y2010.my_info
COURSE_MAP["6.858-2014"] = courses.c6858y2014.my_info
COURSE_MAP["fmsd_hehner"] = courses.fmsd_hehner.my_info

# Maps name to downloaders
DLD_MAP:dict = dict()
DLD_MAP["yt-dlp"] = video_downloader.yt_dlp_downloader()
DLD_MAP["300k"] = video_downloader.default_300k_downloader()

# handle the command arguements
import sys

# Arguments:
# 1. course_id 
# 2. static resources path
# 3. video types, separated by comma
# 4. downloader id 
# 5. verbose (bool)
cmd_args:list = sys.argv[1:]

if (len(cmd_args) != 5):
    print("Invalid number of arguments.")
    exit(-1)

# find the populate_video_maps_list()
course_id:str = cmd_args[0]
if (not course_id in COURSE_MAP):
    print("Invalid course id. It is in the form of <course-number>-year")
    exit(-1)
course_info = COURSE_MAP[course_id]

# find the directory where the extracted static download is stored.
static_root:pathlib.Path = pathlib.Path(cmd_args[1])
if (not static_root.exists() or not static_root.is_dir()):
    print("Invalid directory to the extracted contents.")
    exit(-1)
videos_root:pathlib.Path = static_root.parent 

# parse the video types.
vid_types = cmd_args[2].split(',')

# find the video downloader
downloader:video_downloader
dl_id:str = cmd_args[3]
if (not dl_id in DLD_MAP):
    print("Invalid downloader ID")
    exit(-1)
downloader = DLD_MAP[dl_id]

verbose:bool = str(cmd_args[4])

# Find the video urls after checking the arguments to fail fast.
way_to_get_videos_cls = course_info.get_way_for_downloader(dl_id)
way_to_get_videos = way_to_get_videos_cls(static_root, dl_id)
videos = way_to_get_videos.populate_video_maps_lists(vid_types, verbose)

# Execute the downloading tasks.
start_download(videos, videos_root, downloader, verbose)

