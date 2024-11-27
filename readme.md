# Usage
```
python(3) main.py <course-id> <path-course-content> <video-types> <downloader> <verbose>
```
- `course-id` Identifier of the course. For now, it supports
    + 6.004-2017
    + 18.065-2018
    + 18.06sc-2011
    + 6.034-2010
    + 6.858-2014
- `path-course-content` Path to the static course contents that
  you downloaded from MIT OCW. This does not include the videos,
  but which has the HTML pages that the scripts will scrape to download
  the videos.
- `video_type` Video types to download, separated by comma. For example,
  `Lecture,Recitation`. Usually a course only have these two video types.
  Note that the comma must immediately follow the previous item and immediately
  precede the next item.
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
python3 scripts/main.py "18.065-2018" ~/Videos/18.065-2018/static "Lecture" yt-dlp True
```

## Non-MIT open courses.
Currently, I put some scripts that download open courses from other universities here, too,
because they may reuse some of the code here.

However, since their websites don't necessarily share the same architecture as the MIT
OCW ones, you should only download them using the following commands:

For now, I only have one such script: `./scripts/courses/fmsd_hehner.py`,
which downloads the Lectures, Transcripts, and Slides of the FMSD course 
by Prof. Hehner at the University of Toronto. To use it, execute
```
python3 scripts/main.py "fmsd_hehner" <sub_dir_of_root> <res-types> "300k" <verbose>
```
, where 
- `sub_dir_of_root` is a **sub** directory of the directory where you want the files to be downloaded to.
This strange restriction is because I reuse the code where this argument would be the dir to the static course content.
- `res-types` can be any subset of `{ "Lecture", "Slide", "Transcript" }`. Put a comma between two,
  as described above in the main usage.
- `verbose` same as above in the main usage.

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

- To abstract the process of obtaining (usually by scraping) information about all the downloadable resources of a course,
I define an abstract class `course` that
    - has an abstract method `get_supported_downloaders` which returns a set of supported `video_downloader`s for this course.
    - has an abstract method `populate_video_maps_lists` which returns a dict of `{ vtype : list }`.
        + `vtype: str`
            A type of videos.
        + `list`: `list` of `[ (video_num, url_map) ]`.
            + `video_num`:
                number of the videos for that type.
                For example, `(1, url_map)` for vtype "Lecture"
                means that this `url_map` has the videos for Lecture 1.
            + `url_map`: dict of `{ title : url }`
                title: str
                    Title of a video.
                url: str
                    URL of the video.

- To abstract the information about a course, I define the final class `course_info`
that stores the information. Its constructor takes a list of all subclasses of `course`
that may be used to obtain information about the downloadable resources for this course.
Note that each class in the list obtains the same information (an invariant of the ADTs),
but each class does it in a different way.

- For each course, a script named with the `<course-number>-<year>.py` is written. Inside the script, 
there is a variable `my_info` which is a variable of the type `course_info`.
Additionally, depending on how the information is obtained, subclasses of `course` may be created in
the script.

- There is a central function inside `main.py`: 
`start_download(video_maps: list, videos_root: pathlib.Path, downloader: video_downloader)`.
    - `video_maps` is returned by a `course.populate_video_maps_lists`.
    - `videos_root` is the root directory of where the files are going to be downloaded to.
        - If `videos_root` does not exist, then the function will throw some exception (TBA).
    - For each video type `t` in `video_maps.keys()`
        - For each $i \in$ `range(video_maps[t])`
            - A directory `videos_root/t i+1` is created if it does not exist.
            - calls `downloader.chdir()` on that directory
            - calls `downloader.download()` for each pair in `video_maps[t][i]`.

- The rest of `main.py` is executed when it is executed. That is, the rest acts like a `main()` function in C. 
It will select the `course_info`, the `course` subclass, and the `video_downloader` based on the command line
arguments.
Then, it executes `start_download`.
