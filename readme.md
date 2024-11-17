# Usage
```
python(3) main.py <course-id> <path-course-content> <video-types> <downloader> <verbose>
```
- `course-id` Identifier of the course. For now, it supports
    + 6.004-2017
    + 18.065-2018
    + 18.06sc-2011
    + 6.034-2010
- `path-course-content` Path to the static course contents that
  you downloaded from MIT OCW. This does not include the videos,
  but which has the HTML pages that the scripts will scrape to download
  the videos.
- `video_type` Video types to download, separated by comma. For example,
  `Lecture, Recitation`. Usually a course only have these two video types.
- `downloader` The downloader to use to download the course videos.
  For now, only two are supported:
    + `yt-dlp`: Downloads the course videos from YouTube, usually have 
    better quality than `300k`.
    + `300k`: Downloads the 300k bitrate videos from the Internet Archive.
    Since the bitrate is low, usually they have worse quality than the
    YouTube videos.
-  `verbose`. Outputs more information iff it is True.

## Example
```
python3 main.py "18.065-2018" ~/Videos/18.065-2018/static "Lecture" yt-dlp True
```

# Introduction
MIT OCW is a great platform of free and high-quality educational resources.
From each course there, one can download a bundled course resources, which includes the 
.html files of the course website that can be used offline as well as other resources like .pdf files.

However, probably because of the big size of video and audio resources, they are not included in this bundled download.
Instead, if a course has such resources, in particular, lecture videos, then they will be listed along with the resources as individual videos.

Each MIT course usually has at least 20 lectures, and a lecture may be divided into more than one video, resulting as many as hundreds of videos per course. To manually download all of the videos, one has to click on each video's entry, click download, and save the downloaded video file somewhere.

What makes matters worse is that all videos that can be downloaded this way (i.e. by clicking the download on the dropdown menu from each video on the MIT OCW website) has a low bit rate of 300k. Higher quality versions are instead uploaded and stored on YouTube. Therefore, to obtain a version of higher quality, one has to use some third-party tool (e.g. `youtube-dl`), which adds additional operating time to that of downloading each video.

From the above discussion it is clear that the downloading process of each video is extermely repetitive. Hence, there is ample opportunity of delegating this task to our computers, in the form of scripts.

As a result, this project aims to provide a collection of scripts that automates the process of downloading the lecture videos (and possibly other resources) of many MIT OCW courses. For simplicity, I will refer to the resources as lecture videos.

# Methodology
In this section, I will comprehensively list all the requirements for the scripts and explain how the scripts achieve these goals.

## Requirements

- Assume the user has downloaded the bundled resource and extracted the contents into `.../d/<static>`, where `.../d` is a path to a user designated directory, and `<static>` is anything other than `lectures`
- The scripts will create a directory `.../d/lectures` to store the downloaded lecture videos.
- For each course, the scripts must be able to find all videos that a human can find by looking at the webpages downloaded.
- If there are no videos for the course, then the scripts finish.
- For these videos, the scripts must be able to download all of them in such a way
    - If a video has a YouTube link, then the video is downloaded from there.
    - Otherwise, the 300k bitrate version is downloaded.
- The scripts must additionally be able to group the downloaded videos by which lecture they belong. Specifically,
    - For lecture $i$, a directory `.../d/lectures/Lecture i` is created
    - All videos for it are put into the directory.
- The scripts are able to output information as they do their job.

## Implementation
In this subsection, I will explain how the scripts satisfy the requirements.

- The scripts are written in Python, version 3.

- To abstract the downloading process of a given URL and title, I define an abstract class `video_downloader` that
    - has a field `__dir: pathlib.Path` and another `__dir_filenames: set` that contains all filenames in the dir.
    - has a method `chdir(new_dir: pathlib.Path)` that sets `__dir` to an existing `new_dir` ajd build `__dir_filenames`.
    - has an abstract method `download(title: str, url: str)` that downloads video indicated by `url` into `dir` as a file named by `title`. 
        - If there is already a file with that name (any extension is okay, so that means if the title is in `__dir_filenames`), then the download call does nothing. 
        - After a successful download, the method adds title to `__dir_filenames`.

- There is a central function inside `main.py`: 
`start_download(lecture_video_maps: list, lecture_videos_root: pathlib.Path, downloader: video_downloader)`.
    - Argument `lecture_video_maps` is a map, which maps a video type (e.g. Lecture, Recitation)
        to a list `list`: $[m_l \mid l \in L]$, where
        - $L$ is the set of all lecture numbers.
        - $m_l$ is a 2-tuple, whose first element is `l`, and whose second element is a mapping (`dict`): $\{t \mapsto u\}$, where $t$ is the title of a video, and $u$ is the URL to that video.
        - $m_l$'s are stored in the order of the lectures.
        - If `lecture_video_maps` is empty, then the function will throw some exception (TBA).
        - If any `dict` in the `list` is empty, then the function will throw some exception (TBA).
    - Argument `lecture_videos_root` is the root directory of where the lecture videos are going to be downloaded to.
        - If `lecture_videos_root` does not exist, then the function will throw some exception (TBA).
    - For each $i \in$ `range(lecture_video_maps)`
        - A directory `lecture_videos_root/Lecture i+1` is created if it does not exist.
        - calls `downloader.chdir()` on that directory
        - calls `downloader.download()` for each pair in `lecture_video_maps[i]`.

- For each course, a script named with the `<course-number>-<year>.py` is written. Inside the script, 
    - there is a function `populate_video_maps_list(static_root_path: pathlib.Path)` that returns a list of video maps that can is to be fed into `start_download()`. `static_root_path` is a path to the root of the extracted contents of a bundled download.
    - there is another function `youtube_available()` that returns a boolean to indicate if the videos for this course are available on YouTube.

- The rest of `main.py` is executed when it is executed. That is, the rest acts like a `main()` function in C. The user should supply these things to the script as command-line arguments:
    - Which course videos to download. It is in this format: `<course-number>-<year>`.
    - A path to the directory where the contents of the bundled course content is extracted into. It can be an absolute path or relative path, as it will be passed to a `pathlib.Path` constructor.
    - A string that uniquely identifies a type of downloader to download YouTube videos if they are avialable.
        - For now, only `yt-dlp` is supported.
    - A string that is either True or False to indicate the verbose level.

- `main.py` maintains a map that maps `c<course-number>y<year>` to the `populate_video_maps_list()` defined in `<course-number>-<year>.py`. It maintains another map that maps the names of the YouTube downloaders to instances of the downloaders.

- When the rest is executed, `main.py` selects the corresponding `populate_video_maps_list()` and `video_downloader` from the two maps. It then passes them as well as the path given to `start_download()`, and then executes it.
