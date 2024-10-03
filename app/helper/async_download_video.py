import os
import m3u8
import aiohttp
import asyncio
import shutil
import m3u8.model
from progress.bar import IncrementalBar as IB

from helper.logging_app import logger


class DownloadHLSAsync:
    path: str
    playlist_url: str
    segments: m3u8.model.SegmentList
    __initialized: bool

    def __init__(self, players_list_url: str, path: str):
        """When initializing the class, we get a link to the streaming
        video playlist in the format m3u8, write it to the variable self.playlist_url.
        We take the last link from the list, it has the highest resolution.

        Args:
            playlist_url (str): list of links to video formats m3u8
            path (str): path where the video will be saved
        """

        self.path = path

        try:
            self.playlist_url = m3u8.load(players_list_url).playlists[-1].uri

            # Parse the link using the m3u8 module
            # and collect the video stream elements into a list "segments"
            m3u8_obj = m3u8.load(self.playlist_url)
            self.segments = m3u8_obj.segments

            self.__initialized = True
        except Exception as ex:
            self.__initialized = False
            logger.error(f"Error in class {__class__}: {ex}")

    def __call__(self) -> bool:
        return self.__initialized

    async def download_segment(
        self,
        session: aiohttp.ClientSession,
        segment_url: str,
        index: int,
        output_dir: str,
        progress_bar: IB,
    ) -> None:
        """Asynchronous function to load a single segment.

        Args:
            session (aiohttp.ClientSession): aiohttp session
            segment_url (str): link to video segment
            index (int): index by video segment
            output_dir (str): path to temporary folder for video segments
            progress_bar (progress.bar.IncrementalBar): progress bar
        """

        try:
            async with session.get(segment_url) as response:
                count = 0
                while count < 10:
                    # If you failed to download a video segment, try again.
                    # We have 10 attempts.
                    if response.status == 200:
                        segment_path = os.path.join(output_dir, f"segment_{index}.ts")
                        with open(segment_path, "wb") as f:
                            content = await response.read()
                            f.write(content)
                        break
                    else:
                        count += 1
                        response = session.get(segment_url)
                        logger.error(
                            f"Failed to download segment: {segment_url}. Attempt №{count}"
                        )
                progress_bar.next()
        except Exception as ex:
            logger.error(f"Error downloading segment {index}: {ex}")

    async def download_hls_playlist(self) -> None:
        """The module downloads HLS video."""

        video_path, temp_dir, is_path = self.preparing_dirs(self.path)

        # Check video file existence
        if is_path:
            logger.info(f"File {video_path} has already been downloaded.")
            return

        # Asynchronous loading of all segments
        with IB("Downlod chunks:", max=len(self.segments), width=80) as progress_bar:
            async with aiohttp.ClientSession() as session:
                tasks = list()
                for idx, segment in enumerate(self.segments):
                    segment_url = segment.uri

                    # In case the segments contain relative paths, add the base URL
                    if not segment_url.startswith("http"):
                        segment_url = os.path.join(
                            os.path.dirname(self.playlist_url),
                            segment_url,
                        )

                    tasks.append(
                        self.download_segment(
                            session,
                            segment_url,
                            idx,
                            temp_dir,
                            progress_bar,
                        )
                    )

                # Launch all tasks simultaneously
                await asyncio.gather(*tasks)

        self.merge_segments(video_path, len(self.segments), temp_dir)

        logger.info(f"Скачивание завершено. Видео сохранено в файл: {video_path}")

    @staticmethod
    def preparing_dirs(
        path: str,
        output_file="output_video.ts",
    ) -> tuple[str, str, bool]:
        """The module generates a path to the file and a path to temporary files

        Args:
            path (str): path to parent folder
            output_file (str, optional): video file name. Defaults to "output_video.ts".

        Returns:
            tuple:
                - video_path (str): path to video file
                - temp_dir (str): path to tempary directory of video segments
                - is_path (bool): check if video file exists
        """

        # Form a path to a video file,
        # check if file exists
        video_path = os.path.join(path, output_file)
        is_path = os.path.exists(video_path)

        # Create a temporary folder for segments
        temp_dir = os.path.join(path, "temp_segments")
        if not is_path:
            os.makedirs(temp_dir, exist_ok=True)

        return video_path, temp_dir, is_path

    @staticmethod
    def merge_segments(video_path: str, len_segments: int, temp_dir: str) -> None:
        """Merge segments of video. After delete temporary segment files
        along with the folder.

        Args:
            video_path (str): path to video file
            len_segments (int): list size with segments
            temp_dir (str): path to temporary directory with video segments
        """
        # Merge all segments into a file
        with IB("Merge chunks:", max=len_segments, width=80) as progress_bar:
            with open(video_path, "wb") as f_out:
                for idx in range(len_segments):
                    segment_path = os.path.join(temp_dir, f"segment_{idx}.ts")
                    if os.path.exists(segment_path):
                        with open(segment_path, "rb") as f_in:
                            f_out.write(f_in.read())
                            progress_bar.next()

        # Deleting temporary segment files along with the folder
        shutil.rmtree(temp_dir)

    def run_async(self) -> None:
        """Run async download HLS video"""
        asyncio.run(self.download_hls_playlist())


if __name__ == "__main__":
    m3u8_url = "https://playlist.servicecdn.ru/api/playlist/master/f3ae7682d9952156307f72c6f39cd856/f6de956e62e13fab0311e4e473141544?user-cdn=cdnvideo&acc-id=59148&user-id=400267093&loc-mode=ru&version=17%3A2%3A1%3A0%3A2%3Acdnvideo&consumer=vod&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyLWlkIjo0MDAyNjcwOTN9.CDlwyGyy5kdny9pN3Y4hEN3Y7D_9xvPiElBJvREBUHU"
    path = "./app/downloads/pages"

    download = DownloadHLSAsync(m3u8_url, path)
    if download.is_init:
        download.run_async()
