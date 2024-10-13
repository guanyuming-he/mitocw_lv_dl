import os
import os.path

import pathlib
import requests

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

    def download(self, title: str, url: str, verbose: bool):
        raise NotImplementedError("Abstract method.")
    
class yt_dlp_downloader(video_downloader):
        
        def __init__(self, base_path: pathlib.Path|None = None):
            super(video_downloader, base_path)

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


class default_300k_downloader(video_downloader):

    # The 300k (lowercase k for bits, not bytes) videos are mostly ~100MB (1 hour) or ~200MB (2 hours)
    # A trunk size of 16k is suitable for downloading files of such sizes.
    DEF_TRUNK_SIZE:int = 16*1024
    # Number of retires.
    NUM_RETRIES = 8

    def __init__(self, base_path: pathlib.Path|None = None):
        super(video_downloader, base_path)

    def download(self, title: str, url: str, verbose: bool = False):
        if(title in self._dir_filenames):
            if(verbose):
                print(title + " has already been downloaded. Skipping...")
            return

        for i in range(NUM_RETRIES):
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Check for HTTP errors

                # calculate the file name.
                ext:str = url[url.rindex('.'):] # Extension is from the last '.' in the url to the end
                # rindex() will raise an Exception if it can not be found, so I don't have to.
                filename:str = title+ext
                
                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=DEF_TRUNK_SIZE):
                        file.write(chunk)
                
                # Success
                if verbose:
                    print(f"Downloaded 300k video to {filename}")
                # and don't forget to update the filenames set
                self._dir_filenames.add(title)
                break

            except Exception as e:
                if verbose:
                    print("An error occurred while downloading. Retrying...")
                continue

