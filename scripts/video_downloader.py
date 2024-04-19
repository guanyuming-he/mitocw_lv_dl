import os
import os.path

import pathlib

class video_downloader:

    def __init__(self, base_path: pathlib.Path|None):
        self._dir:pathlib.Path = None
        self._dir_filenames:set = None

        if (base_path is None):
            return
        self.chdir(base_path)

    def chdir(self, new_path: pathlib.Path) -> None:
        if(not new_path.exists() or not new_path.is_dir()):
            raise ValueError("The path you provided does not exist or is not to a directory.")
        
        self._dir = new_path
        # Now build a directory filenames set
        # because I don't want to list the directory contents once per download.
        self._dir_filenames = set()
        f: pathlib.Path
        for f in self._dir.iterdir():
            if f.exists() and f.is_file():
                # file name without extension
                file_name_no_ext = os.path.splitext(f.name)[0]
                self._dir_filenames.add(file_name_no_ext)

    def download(self, title: str, url: str):
        raise NotImplementedError("Abstract method.")
    
class yt_dlp_downloader(video_downloader):
        
        def __init__(self):
            super(video_downloader, None)

        def __generate_command(self, url: str, title: str) -> str:
            command:str = "yt-dlp -o "

            output_path = self._dir / (title + ".%(ext)s")
            # append the output path
            command += ('\"' + output_path.absolute().as_posix() + '\"')
            # append the youtube URL
            command += " " + url

            return command

        def download(self, title: str, url: str, verbose:bool = False) -> None:
            # Check if the file with the title already exists
            if(title in self._dir_filenames):
                if(verbose):
                    print(title + " has already been downloaded. Skipping...")
                return

            # Now the file has not been downloaded before.
            # Just execute the command
            cmd:str = self.__generate_command(url, title)
            if(verbose):
                print("Executing command: " + cmd)
            os.system(cmd)

            # and don't forget to update the filenames set
            self._dir_filenames.add(title)