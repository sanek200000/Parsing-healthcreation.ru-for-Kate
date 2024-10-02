import os
import m3u8
import aiohttp
import asyncio
import shutil
from helper.logs import logger


class DownloadHLSAsync:
    def __init__(self, players_list_url: str, path: str) -> None:
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

    @property
    def initialized(self):
        return self.__initialized

    async def download_segment(
        self,
        session: aiohttp.ClientSession,
        segment_url: str,
        index: int,
        output_dir: str,
    ) -> None:
        """Асинхронная функция для загрузки одного сегмента."""

        try:
            async with session.get(segment_url) as response:
                if response.status == 200:
                    segment_path = os.path.join(output_dir, f"segment_{index}.ts")
                    with open(segment_path, "wb") as f:
                        content = await response.read()
                        f.write(content)
                    print(f"Сегмент {index} успешно скачан.")
                else:
                    logger.error(
                        f"Ошибка при скачивании сегмента {index}: {response.status}"
                    )
        except Exception as ex:
            logger.error(f"Ошибка при скачивании сегмента {index}: {ex}")

    async def download_hls_playlist(self) -> None:
        video_path, temp_dir, is_path = self.preparing_dirs(self.path)

        # Check video file existence
        if is_path:
            logger.info(f"File {video_path} has already been downloaded.")
            return

        # Asynchronous loading of all segments
        async with aiohttp.ClientSession() as session:
            tasks = list()
            for i, segment in enumerate(self.segments):
                segment_url = segment.uri

                # In case the segments contain relative paths, add the base URL
                if not segment_url.startswith("http"):
                    segment_url = os.path.join(
                        os.path.dirname(self.playlist_url),
                        segment_url,
                    )

                tasks.append(self.download_segment(session, segment_url, i, temp_dir))

            # Launch all tasks simultaneously
            await asyncio.gather(*tasks)

        self.merge_segments(video_path, len(self.segments), temp_dir)

        logger.info(f"Скачивание завершено. Видео сохранено в файл: {video_path}")

    @staticmethod
    def preparing_dirs(path: str, output_file="output_video.ts") -> tuple:
        # Form a path to a video file
        video_path = os.path.join(path, output_file)
        is_path = os.path.exists(video_path)

        # Create a temporary folder for segments
        temp_dir = os.path.join(path, "temp_segments")
        os.makedirs(temp_dir, exist_ok=True)

        return video_path, temp_dir, is_path

    @staticmethod
    def merge_segments(video_path, len_segments, temp_dir) -> None:
        # TODO: добавить прогрессбар
        # Объединение всех сегментов в один файл
        print("Объединение всех сегментов в один файл")
        with open(video_path, "wb") as f_out:
            for i in range(len_segments):
                segment_path = os.path.join(temp_dir, f"segment_{i}.ts")
                print(f"{segment_path = }")
                if os.path.exists(segment_path):
                    with open(segment_path, "rb") as f_in:
                        f_out.write(f_in.read())

        # Deleting temporary segment files along with the folder
        shutil.rmtree(temp_dir)

    def run_async(self) -> None:
        asyncio.run(self.download_hls_playlist())


if __name__ == "__main__":
    m3u8_url = "https://playlist.servicecdn1.ru/api/playlist/master/f3ae7682d9952156307f72c6f39cd856/f6de956e62e13fab0311e4e473141544?user-cdn=cdnvideo&acc-id=59148&user-id=400267093&loc-mode=ru&version=17%3A2%3A1%3A0%3A2%3Acdnvideo&consumer=vod&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyLWlkIjo0MDAyNjcwOTN9.CDlwyGyy5kdny9pN3Y4hEN3Y7D_9xvPiElBJvREBUHU"
    path = "./app/downloads/pages"

    download = DownloadHLSAsync(m3u8_url, path)
    if download.initialized:
        download.run_async()
