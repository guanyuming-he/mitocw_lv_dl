from . import course
from pathlib import Path

# Seems Python doesn't like me to put static variables
# inside classes.
# Hence, I will just put them in this file,
# as no other class will use them.
NUM_LECTURES = 34
RES_TYPES = [ "Lecture", "Transcript", "Slide" ]
URL_HEADS = {
    RES_TYPES[0]: "https://www.cs.toronto.edu/~hehner/FMSD/FMSD",
    RES_TYPES[1]: "https://www.cs.toronto.edu/~hehner/FMSD/talk",
    RES_TYPES[2]: "https://www.cs.toronto.edu/~hehner/FMSD/show",
}
URL_TAILS = {
    RES_TYPES[0]: ".mp4",
    RES_TYPES[1]: ".pdf",
    RES_TYPES[2]: ".pdf",
}

# The 300k downloader can not just download videos,
# but actually any file over HTTP(S).
class fmsd_hehner(course.course):
    """
    Final class for downloading FMSD by Prof. Hehner
    at the University of Toronto.

    It cannot inherit from three_100k_course
    because it would break its invariant.
    Instead, inherit from the most base class.
    """
    def get_supported_downloaders() -> set:
        return { "300k" }

    def __init__(
        self, res_path: Path, downloader_type: str
    ):
        """
        Parameters
        ----------
        res_path: Path
            path to the directory where the files will
            be downloaded to.

        downloader_type: str
            must be 300k.
        """
        if downloader_type != "300k":
            raise ValueError("downloader type must be 300k.")

        super().__init__(res_path, downloader_type)

    def populate_video_maps_lists(self, types: set, verbose) -> dict:
        """
        Populates a dict of { vtype : list }.
        vtype: str
            A type of videos.
        list: list of [ (video_num, url_map) ].
            video_num:
                number of the videos for that type.
                For example, (1, url_map) for vtype "Lecture"
                means that this url_map has the videos for Lecture 1.
            url_map: dict of { title : url }
                title: str
                    Title of a video.
                url: str
                    URL of the video.

        Parameters
        ----------
        types: set
            A set of video types to download.

        Returns
        -------
        The dict explained above.

        Raises
        ------
        ValueError
            if an element in types is not supported by this course.
        """
        ret = dict()

        for t in types:
            if t not in RES_TYPES:
                raise ValueError(
                    f"{t} is not a supported resource type." + \
                    f"supported: {RES_TYPES}"
                )

            ls_vids = [
                (
                    i, 
                    { f"{t} {i}": URL_HEADS[t] + str(i) + URL_TAILS[t] }
                )
                for i in range(NUM_LECTURES)
            ]
            
            ret[t] = ls_vids

        return ret


my_info = course.course_info([fmsd_hehner])
