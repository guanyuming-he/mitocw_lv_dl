import os
import os.path

import pathlib

class video_downloader:

    def __init__(self, base_path: pathlib.Path):
        self.chdir(base_path)

    def chdir(self, new_path: pathlib.Path):
        if(not new_path.exists() or not new_path.is_dir()):
            raise ValueError("The path you provided does not exist or is not to a directory.")
        
        self.__dir = new_path
        # Now build a directory filenames set
        # because I don't want to list the directory contents once per download.
        self.__dir_filenames: set = set()
        f: pathlib.Path
        for f in self.__dir.iterdir():
            if f.exists() and f.is_file():
                # file name without extension
                file_name_no_ext = os.path.splitext(f.name)[0]
                self.__dir_filenames.add(file_name_no_ext)

    def download(self, url: str, title: str):
        raise NotImplementedError("Abstract method.")
    
class yt_dlp_downloader(video_downloader):
        
        def __init__(self, base_path: pathlib.Path):
            super(base_path)

        def __generate_command(self, url: str, title: str):
            raise NotImplementedError()

        def download(self, url: str, title: str):
            # Check if the file with the title already exists
            if(title in self.__dir_filenames):
                return

            # Now the file has not been downloaded before.
            # Just execute the command
            os.system(self.__generate_command(url, title))

            # and don't forget to update the filenames set
            self.__dir_filenames.add(title)