import video_downloader
import pathlib

def start_download(
    lecture_videos_map: dict, 
    lecture_videos_root: pathlib.Path, 
    downloader: video_downloader.video_downloader,
    verbose:bool = False
) -> None:
    """
    :param lecture_videos_map This parameter is a map of lists. It maps the string describing a kind of videos 
    (e.g. lecture, recitation, mega-recitation, tutorial) to a list of that kind of videos.
    Each such list is a list of maps. Each map contains all videos of an espisode. For example, 
    if a list is for lecture videos, then that list[0] is a map that contains all videos for lecture 0+1.
    Inside any of such map, video titles are mapped to their URLs (could be a youtube url or an ordinary 300k url).
    """
    
    if len(lecture_videos_map) == 0:
        raise ValueError("The videos map is empty.")
    if not lecture_videos_root.exists() or not lecture_videos_root.is_dir():
        raise ValueError("The root for videos downloaded does not exist or is not a directory.")
    if downloader is None:
        raise ValueError("The downloader is none.")
    
    kind:str
    v_list:list
    for (kind, v_list) in lecture_videos_map.items():
        for i in range(len(v_list)):
            # Lectures are indexed from 1
            li = i+1

            if (verbose):
                print("downloading videos for " + kind + ' ' + str(li))

            lecture_video_dir: pathlib.Path = lecture_videos_root / (kind + " " + str(li))
            # If the lecture video folder does not exist,
            # then create it.
            if(not lecture_video_dir.exists() or not lecture_video_dir.is_dir()):
                lecture_video_dir.mkdir(exist_ok=True)

            downloader.chdir(lecture_video_dir)

            video_map:dict = v_list[i]
            title:str
            for (title, url) in video_map.items():
                # Replace illegal filename characters with #
                title = title.replace('/', '#')
                title = title.replace(':', '#')
                title = title.replace('\"', '#')
                title = title.replace('?', '#')
                title = title.replace('*', '#')
                downloader.download(title, url, verbose)

# Import courses
import courses.c6004y2017
import courses.c1802scy2010

# Maps <course-number>-<year> to (populate_video_maps_list,  youtube_available)
COURSE_MAP:dict = dict()
COURSE_MAP["6.004-2017"] = (courses.c6004y2017.populate_video_maps_list, courses.c6004y2017.youtube_available)
COURSE_MAP["18.02sc-2010"] = (courses.c1802scy2010.populate_video_maps_list, courses.c1802scy2010.youtube_available)

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
LECTURE_VIDEOS_ROOT:pathlib.Path = STATIC_ROOT.parent / "lectures"
LECTURE_VIDEOS_ROOT.mkdir(exist_ok=True)

# find the video downloader
downloader:video_downloader
if(COURSE_MAP[COURSE_ID_ARG][1]()): # If youtube videos are available
    YT_DL_ID:str = COMMAND_ARGS[2]
    if (not YT_DL_ID in YT_DL_MAP):
        print("Invalid downloader ID")
        exit(-1)
    downloader = YT_DL_MAP[YT_DL_ID]
else: # youtube videos are not available. Fallback to 300k downloader
    raise NotImplemented("Not implemented yet.")

VERBOSE:bool = str(COMMAND_ARGS[3])

# Execute the download
start_download(COURSE_VIDEO_MAPS_POPULATOR(STATIC_ROOT, VERBOSE), LECTURE_VIDEOS_ROOT, downloader, VERBOSE)
