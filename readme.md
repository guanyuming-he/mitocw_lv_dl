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

- First, the scripts must be able to download the bundled course resource given the link to that course on MIT OCW.
- Then, the scripts must be able to extract the contents into a subdirectory inside a user designated local directory, say `.../d/static`, where `.../d` is the path to the user designated directory `d`, and the files are extracted into a new directory `static` inside it.
- Besides, the scripts will create another directory `.../d/lectures` to store the downloaded lecture videos.
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

- To abstract the downloading process of a given URL and title, I define absstract class `video_downloader`
    - has a field `__dir: pathlib.Path` and another `__dir_filenames: set` that contains all filenames in the dir.
    - has a method `chdir(new_dir: pathlib.Path)` that sets `__dir` to an existing `new_dir` ajd build `__dir_filenames`.
    - has an abstract method `download(url: str, title: str)` that downloads video indicated by `url` into `dir` as a file named by `title`. 
        - If there is already a file with that name (any extension is okay, so that means if the title is in `__dir_filenames`), then the download call does nothing. 
        - After a successful download, the method adds title to `__dir_filenames`.

- There is a central function 
`start_download(lecture_video_maps: list, lecture_videos_root: pathlib.Path, downloader: video_downloader)`.
    - Argument `lecture_video_maps` is a `list`: $[m_l \mid l \in L]$, where
        - $L$ is the set of all lectures
        - $m_l$ is a mapping (`dict`): $\{t \mapsto u\}$, where $t$ is the title of a video, and $u$ is the URL to that video.
        - $m_l$'s are stored in the order of the lectures.
        - If `lecture_video_maps` is empty, then the function will throw some exception (TBA).
        - If any `dict` in the `list` is empty, then the function will throw some exception (TBA).
    - Argument `lecture_videos_root` is the root directory of where the lecture videos are going to be downloaded to.
        - If `lecture_videos_root` does not exist, then the function will throw some exception (TBA).
    - For each $i \in$ `range(lecture_video_maps)`
        - A directory `lecture_videos_root/Lecture i+1` is created if it does not exist.
        - calls `downloader.chdir()` on that directory
        - calls `downloader.download()` for each pair in `lecture_video_maps[i]`.
