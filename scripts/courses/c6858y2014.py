import pathlib
import bs4
import re

from . import helpers
from . import course

class c6858_gallery(course.video_gallery_course):

    def __init__(self, res_path: pathlib.Path, downloader_type: str):
        super().__init__(
            res_path, downloader_type,
            { "Lecture" : "video-lectures" }
        )

my_info = course.course_info([course.three_100k_course, c6858_gallery])
