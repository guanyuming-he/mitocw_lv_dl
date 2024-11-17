"""
course.py provides the base classes of all courses.

course:
    Representing a way to retrieve video information.
    Base class of all.

three_100k_course:
    Representing the way that retrieves information
    of the 300k bitrate videos.
    All courses should support this.

video_gallery_course:
    For all courses that have a video_galleries directory
    in their static resources,
    this class can be used as the way to retrieve information
    from these gallery folders.

course_info:
    A final (i.e. cannot have subclasses) 
    class of information about a course.
    It contains information about which ways of retrieving
    information are available for a course,
    which downloaders are supported, 
    and for a given downloader, it will choose the way to retrieve
    information.

"""

from pathlib import Path
from . import helpers


class course:
    """
    Abstract base class course.
    Handles the retrieval of all the video information from
    a course's resources (html files, etc.)

    The information will be passed to a downloader to start the downloading.

    Invariant:
        self.res_path points to the static resources of a valid course.
        self.downloader_type is compatible with this class's
        way of retrieving information.

    """

    ####################### Static Methods ########################

    def get_supported_downloaders() -> set:
        """
        Returns
        -------
        The set of all supported downloaders for this way of retrieving information.
        """
        raise NotImplementedError("abstract static method.")

    ####################### Instance Methods ########################

    def __init__(self, res_path: Path, downloader_type: str):
        """
        Parameters
        ----------
        res_path: Path
            a path to the static resources of the course.

        downloader_type: str
            the type of the downloader. 
            This parameter will decide the video urls output by this class.
            For example, if str == "yt-dlp", then the urls are YouTube urls.
            if str == "300k", then the urls are linked to the 300k versions.
        """
        # I assume that the path will be checked
        # in some control flow above.
        # Ideally, that is when the path is input by the user.
        # So I don't need to check here.
        self.res_path = res_path
        # For this one, it is checked inside each subclass.
        # I can't know now which downloader is compatible with each course.
        self.downloader_type = downloader_type

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
        raise NotImplementedError("abstract method")


# Can't start with a number, hence this awkward name.
class three_100k_course(course):
    """
    All courses that have videos should have 300k bitrate videos.
    This class is for downloading them.
    """

    ####################### Static Methods ########################

    def get_supported_downloaders() -> set:
        """
        Returns
        -------
        The set of all supported downloaders for this way of retrieving information.
        """
        return { "300k" }

    ####################### Instance Methods ########################

    def __init__(
        self, res_path: Path, downloader_type: str,
        # where directory name is the directory of the resource of
        # that video type.
        #
        # Theoretically, each course may have different names,
        # So I maintain one for each course.
        # In practice, all courses I have encountered until now
        # follow this convention.
        # If somehow in the future some course doesn't (e.g. because of a typo),
        # just create another this variable in a subclass.
        resources: dict = {
            "Lecture"           : "lecture-videos",
            "Recitation"        : "recitation-videos",
            # Only a few courses have this. Comment it out.
            # Let those who have it add it to this variable.
            #"Mega-Recitation"   : "mega-recitation-videos"
        }
    ):
        """
        Parameters
        ----------
        res_path: Path
            a path to the static resources of the course.

        downloader_type: str
            For this type of course, 300k

        resources: dict of { vt : dir }
            video type mapping to directory name.
            In principle, this should be a static variable.
            However, in each script run only one class
            instance will be created anyway.
            Hence, might as well let it be an instance variable.
        """
        if downloader_type not in three_100k_course.get_supported_downloaders():
            raise ValueError(
                "downloader type not supported. Supported types:" + \
                f"{three_100k_course.get_supported_downloaders()}"
            )

        super().__init__(res_path, downloader_type)

        self.__resources = resources

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

        res_res_path = self.res_path / "resources"
        # this course has video resources for me to use this base class!
        assert res_res_path.exists() and res_res_path.is_dir()

        ret: dict = {}

        for t in types:
            
            if t not in self.__resources:
                raise ValueError(
                    "The video type is not supported by this course" + \
                    f"Supported ones: {self.__resources.keys()}"
                )

            ind_html_path = res_res_path / self.__resources[t] / "index.html"
            ind_bs:bs4.BeautifulSoup = helpers.give_me_bs(ind_html_path)

            list_vids = helpers.grab_title_url_from_300k_resources_index_html(
                ind_bs, t, verbose
            )
            # Add lecture numbers to the list
            list_vids = [
                (i+1, list_vids[i]) for i in range(len(list_vids))
            ]

            ret[t] = list_vids

        return ret


class video_gallery_course(course):
    """
    Many courses have a dedicated video_galleries directory,
    which contains gallery directories.
    
    Each gallery directory contains an index.html of a specific video type.
    This class populates the video maps list by using the gallery HTMLs.

    Invariant:
        downloader_type must be "yt-dlp"
    """

    ####################### Static Methods ########################

    def get_supported_downloaders() -> set:
        """
        Returns
        -------
        The set of all supported downloaders for this way of retrieving information.
        """
        # For now, only support yt-dlp for downloading youtube videos.
        return { "yt-dlp" }

    ####################### Instance Methods ########################

    def __init__(
        self, res_path: Path, downloader_type: str,
        galleries: dict = {
            "Lecture"           : "lecture-videos",
            "Recitation"        : "recitation-videos",
            # Only a few courses have this. Comment it out.
            # Let those who have it add it to this variable.
            #"Mega-Recitation"   : "mega-recitation-videos"
        }
    ):
        """
        Parameters
        ----------
        res_path: Path
            a path to the static resources of the course.

        downloader_type: str
            the type of the downloader. 
            This type of courses store youtube urls in their video_galleries.
            Therefore, str cannot be "300k"

        galleries: dict of { vt : dir },
            where vt is video type, dir is directory name in the gallery directory.
            In principle, this should be a static variable.
            However, in each script run only one class
            instance will be created anyway.
            Hence, might as well let it be an instance variable.
        """
        if downloader_type not in video_gallery_course.get_supported_downloaders():
            raise ValueError(
                "downloader type not supported. Supported types:" + \
                f"{video_gallery_course.get_supported_downloaders()}"
            )

        super().__init__(res_path, downloader_type)

        # { vtype : directory name }
        # where directory name is the directory of the gallery of
        # that video type.
        #
        # Theoretically, each course may have different names,
        # So I maintain one for each course.
        # In practice, all courses I have encountered until now
        # follow this convention.
        # If somehow in the future some course doesn't (e.g. because of a typo),
        # just create another this variable in a subclass.
        self.__galleries = galleries

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

        galleries_path = self.res_path / "video_galleries"
        # this course has video galleries for me to use this base class!
        assert galleries_path.exists() and galleries_path.is_dir()

        ret: dict = {}

        for t in types:
            
            if t not in self.__galleries:
                raise ValueError(
                    "The video type is not supported by this course" + \
                    f"Supported ones: {self.__galleries.keys()}"
                )

            ind_html_path = galleries_path / self.__galleries[t] / "index.html"
            ind_bs:bs4.BeautifulSoup = helpers.give_me_bs(ind_html_path)

            # Get the html pages of the videos.
            list_html_paths:list = helpers.grab_html_from_galleries_index_html(
                ind_bs, ind_html_path.parent, verbose
            )
            list_vids:list = []

            # turn each html page into a map of title -> url
            for hp in list_html_paths:
                bs = helpers.give_me_bs(hp)
                tit_url_map = helpers.grab_title_url_from_youtube_html_page(
                    bs, t, verbose
                )
                list_vids.append(tit_url_map)

            # Add numbers to the list, starting from 1.
            # Limitation: In practice, videos of some number may be missing.
            # For example, we may have Lecture 1,2,3,5,6,...
            # Possible solution: auto detection from title, or manually provide
            # the numbers.
            list_vids = [
                (i+1, list_vids[i]) for i in range(len(list_vids))
            ]

            ret[t] = list_vids

        return ret


class course_info:

    def __init__(self, ls_ways: list):
        """
        Parameters:
        ls_ways: list
            list of possible ways (subclass of course) to retrieve information
            for this course.
        """
        self.ls_ways = ls_ways
        assert len(ls_ways) > 0

        self.downloaders:set = set()
        self.map_dld_ways:dict = dict()

        for w in ls_ways:
            if not issubclass(w, course):
                raise TypeError(
                    "ls_ways must be a list of subclasses of course."
                )

            # supported downloaders is the union of the supported
            # dlds for each way.
            dlds = w.get_supported_downloaders()
            self.downloaders = self.downloaders ^ dlds

            # For now, suppose each way's set of downloaders is disjoint from the others.
            for dld in dlds:
                self.map_dld_ways[dld] = w
    
    def get_supported_downloaders(self):
        return self.downloaders

    def get_way_for_downloader(self, dld: str):
        if dld not in self.map_dld_ways:
            raise ValueError(
                "This downloader is not supported." + \
                f"Supported: {self.downloaders}"
            )

        return self.map_dld_ways[dld]

