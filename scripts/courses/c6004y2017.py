import pathlib
import bs4
import json

from . import course
from . import helpers


# Unfortunately, this course has neither 300k nor video galleries.
# I have to do it the hard way.

class c6004_yt(course.course):

    def get_supported_downloaders() -> set:
        """
        Returns
        -------
        The set of all supported downloaders for this way of retrieving information.
        """
        # This course only has youtube videos.
        return { "yt-dlp" }

    def populate_video_maps_lists(self, types: set) -> dict:
    
        # Only lecture videos are available in this course.
        if types != { "Lecture" }:
            raise TypeError(
                "Unsupported video types." + \
                "Supported: Lecture"
            )

        NUM_LECTURERS = 21

        # 1. to fill the video_maps_list, first I must find all video .html file for each lecture.
        # lecture index -> list of .html file paths
        video_html_file_path_list = []
        
        i0 = 0
        for i0 in range(NUM_LECTURERS):
            # lecture index = i
            # path is root/pages/ci/cis2
            # each video is contained inside path/cis2vj as index.html,
            # where j is the video index
            i = i0+1
            lecture_videos_path : pathlib.Path = static_root_path / "pages"
            lecture_videos_path /= ('c' + str(i) + '/' + 'c' + str(i) + "s2")
            video_dirs = [
                dir 
                for dir in lecture_videos_path.iterdir() 
                if dir.is_dir()
            ]
            temp = []
            for dir in video_dirs:
                v_path = pathlib.Path(dir) / "index.html"
                assert (v_path.exists())
                temp.append(v_path)
            video_html_file_path_list.append(temp)

        # 2. from each .html file find the video title and URL
        video_maps_list:list = list()

        i0 = 0
        for i0 in range(NUM_LECTURERS):
            # Lecture index starts from 1
            i = i0+1

            videos_map = {}

            html_paths:list = video_html_file_path_list[i0]
            for html_path in html_paths:
                bs = helper.give_me_bs(html_path)


                videos_map.update(
                    helpers.grab_title_url_from_youtube_html_page(
                        bs, "Lecture", verbose
                    )
                )

            video_maps_list.append((i, videos_map))

        if(verbose):
            print("video_maps_list=")
            print(video_maps_list)

        # Only lectures are available for this course.
        return {"Lecture" : video_maps_list}


my_info = course.course_info([c6004_yt])
