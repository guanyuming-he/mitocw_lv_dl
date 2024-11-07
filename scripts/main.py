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
    creating a subdirectory for each lecture.
    The downloading will be done using downloader.

        Parameters:
            video_maps (map): map of lists of tuples. 
                Each key is the name of type of videos (e.g. "Lecture", "Recitation")
                Each key is mapped to a list of tuples.
                Each element in the list is a 2-tuple,
                whose first element is the video number,
                and whose second element is a map that maps titles to video urls. 
                The maps are arranged in the order that the videos are given.
            videos_root (pathlib.Path):
                path to the directory where all the videos downloaded 
                are to be placed in.
            downloader:
                The ADT that handles the downloading.

        Requires:
            The maps is not empty; the video urls are valid.({char: '#' for char in illegal_chars})
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
        raise ValueError("The video maps is empty.")
    if not videos_root.exists() or not videos_root.is_dir():
        raise ValueError("The root for videos downloaded does not exist or is not a directory.")
    if downloader is None:
        raise ValueError("The downloader is none.")
    
    video_type:str
    for video_type in video_maps:
        video_type_dir = videos_root / (video_type + 's')
        list_video_maps: list = video_maps[video_type]
        if(not video_type_dir.exists() or not video_type_dir.is_dir()):
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

# Maps <course-number>-<year> to (populate_video_maps_list,  youtube_available)
COURSE_MAP:dict = dict()
COURSE_MAP["6.004-2017"] = (courses.c6004y2017.populate_video_maps_list, courses.c6004y2017.youtube_available)
COURSE_MAP["18.065-2018"] = (courses.c18065y2018.populate_video_maps_list, courses.c18065y2018.youtube_available)
# for now the internet archive is down. Use the YouTube version, even if they are 300k, too.
COURSE_MAP["18.06sc-2011"] = (courses.c1806scy2011.populate_video_maps_list_youtube, courses.c1806scy2011.youtube_available_true)
COURSE_MAP["6.034-2010"] = (courses.c6034y2010.populate_video_maps_list, courses.c6034y2010.youtube_available)

# Maps name to YouTube downloaders
YT_DL_MAP:dict = dict()
YT_DL_MAP["yt-dlp"] = video_downloader.yt_dlp_downloader()

# handle the command arguements
import sys

COMMAND_ARGS:list = sys.argv[1:]

if (len(COMMAND_ARGS) != 4):
    print("Invalid number of arguments.")
    exit(-1)

# find the populate_video_maps_list()
COURSE_ID_ARG:str = COMMAND_ARGS[0]
if (not COURSE_ID_ARG in COURSE_MAP):
    print("Invalid course id. It is in the form of <course-number>-year")
    exit(-1)
COURSE_VIDEO_MAPS_POPULATOR = COURSE_MAP[COURSE_ID_ARG][0]

# find the directory where the extracted static download is stored.
STATIC_ROOT:pathlib.Path = pathlib.Path(COMMAND_ARGS[1])
if (not STATIC_ROOT.exists() or not STATIC_ROOT.is_dir()):
    print("Invalid directory to the extracted contents.")
    exit(-1)
VIDEOS_ROOT:pathlib.Path = STATIC_ROOT.parent 

# find the video downloader
downloader:video_downloader
DL_ID:str = COMMAND_ARGS[2]
if(COURSE_MAP[COURSE_ID_ARG][1]()): # If youtube videos are available
    if (not DL_ID in YT_DL_MAP):
        print("Invalid downloader ID")
        exit(-1)
    downloader = YT_DL_MAP[DL_ID]
else: # youtube videos are not available. Fallback to 300k downloader
    if DL_ID != "300k":
        print("For this course only 300k videos are avialable")
        exit(-1)
    downloader = video_downloader.default_300k_downloader()

VERBOSE:bool = str(COMMAND_ARGS[3])

# Execute the downloading tasks.
start_download(COURSE_VIDEO_MAPS_POPULATOR(STATIC_ROOT, VERBOSE), VIDEOS_ROOT, downloader, VERBOSE)

