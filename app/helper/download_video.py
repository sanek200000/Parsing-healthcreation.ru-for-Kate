import os
import m3u8
from requests import Session
from helper.logging import logger


class DownloadHLS:
    def __init__(self, playlist_url: str, path: str) -> None:
        """When initializing the class, we get a link to the streaming
        video playlist in the format m3u8, write it to the variable self.playlist_url.
        We take the last link from the list, it has the highest resolution.

        Args:
            playlist_url (str): list of links to video formats m3u8
            path (str): path where the video will be saved
        """
        self.path = path
        self.playlist_url = m3u8.load(playlist_url).playlists[-1].uri
        logger.info(f"Download video path: {self.path}, url: {self.playlist_url}")

    def get_hls_video(self, session: Session, output_file="output_video.ts") -> str:
        """The module downloads HLS video.

        Args:
            session (Session): requests session
            output_file (str, optional): video file name. Defaults to "output_video.ts".

        Returns:
            str: information about download results
        """

        # Form a path to a video file and check its existence
        video_path = os.path.join(self.path, output_file)
        if os.path.exists(video_path):
            logger.info(f"File {video_path} has already been downloaded.")
            return f"File {video_path} has already been downloaded."

        # If the file does not exist, we parse the link using the m3u8 module
        # and collect the video stream elements into a list "segments"
        m3u8_obj = m3u8.load(self.playlist_url)
        segments = m3u8_obj.segments

        # Open the file to save the downloaded information into it.
        with open(video_path, "wb") as f_out:
            # We go through each segment of the list of parts of the video stream,
            # download and save to a file
            for i, segment in enumerate(segments):
                segment_url = segment.uri

                # In case the segments contain relative paths, add the base URL
                if not segment_url.startswith("http"):
                    segment_url = os.path.join(
                        os.path.dirname(self.playlist_url),
                        segment_url,
                    )

                # TODO: попробовать многопоточный request

                # get response by segment
                response = session.get(segment_url)
                print(f"Downloading the segment {i+1}/{len(segments)}: {segment_url}")
                # logger.info(f"Downloading the segment {i+1}/{len(segments)}: {segment_url}")

                count = 0
                while count < 10:
                    # If you failed to download a video segment, try again.
                    # We have 10 attempts.
                    if response.status_code == 200:
                        # write the response to the file and exit the loop
                        f_out.write(response.content)
                        break
                    else:
                        count += 1
                        response = session.get(segment_url)
                        logger.debug(
                            f"Failed to download segment: {segment_url}. Attempt №{count}"
                        )

        logger.info(f"Download complete, video saved to file: {video_path}")
        return f"Download complete, video saved to file: {video_path}"
