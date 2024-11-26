import video_downloader
import pathlib


NUM_LECTURES = 34
URL_HEADS = {
    "Lecture": "https://www.cs.toronto.edu/~hehner/FMSD/FMSD",
    "Transcript": "https://www.cs.toronto.edu/~hehner/FMSD/talk",
    "Slide": "https://www.cs.toronto.edu/~hehner/FMSD/show",
}
URL_TAILS = {
    "Lecture": ".mp4",
    "Transcript": ".pdf",
    "Slide": ".pdf",
}


if __name__ == "__main__":
    downloader = video_downloader.default_300k_downloader()

    # handle the command arguements
    import sys

    # Arguments:
    # 1. directory to download the files to.
    # 2. verbose
    cmd_args:list = sys.argv[1:]
    if (len(cmd_args) != 2):
        print("2 arguments are expected.")
        exit(-1)

    root_dir = pathlib.Path(cmd_args[0])
    verbose = bool(cmd_args[1])

    # One may wish to switch the order of the two for loops.
    # However, as that involves the expensive downloader.chdir,
    # I will have to do them this way only.
    for t in { "Lecture", "Transcript", "Slide" }:
        # Create a directory for each file type.
        cur_dir = root_dir / (t + 's')
        cur_dir.mkdir(exist_ok=True)
        downloader.chdir(cur_dir)

        for i in range(NUM_LECTURES):
            downloader.download(
                t + f" {i}",
                URL_HEADS[t] + str(i) + URL_TAILS[t],
                verbose
            )
