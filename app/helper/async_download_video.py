import os
import m3u8
import aiohttp
import asyncio
import shutil


class AsyncDownloadHLS:
    def __init__(self, playlist_url: str, path: str) -> None:
        self.path = path
        self.playlist_url = m3u8.load(playlist_url).playlists[-1].uri

    async def download_segment(self, session, segment_url, index, output_dir):
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
                    print(f"Ошибка при скачивании сегмента {index}: {response.status}")
        except Exception as e:
            print(f"Ошибка при скачивании сегмента {index}: {e}")

    async def download_hls_playlist(self, output_file="output_video.ts") -> None:
        # Form a path to a video file and check its existence
        video_path = os.path.join(self.path, output_file)
        if os.path.exists(video_path):
            # logger.info(f"File {video_path} has already been downloaded.")
            return f"File {video_path} has already been downloaded."

        # If the file does not exist, we parse the link using the m3u8 module
        # and collect the video stream elements into a list "segments"
        m3u8_obj = m3u8.load(self.playlist_url)
        segments = m3u8_obj.segments

        # Создаем временную папку для сегментов
        temp_dir = os.path.join(self.path, "temp_segments")
        os.makedirs(temp_dir, exist_ok=True)

        # Асинхронная загрузка всех сегментов
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, segment in enumerate(segments):
                segment_url = segment.uri

                # In case the segments contain relative paths, add the base URL
                if not segment_url.startswith("http"):
                    segment_url = os.path.join(
                        os.path.dirname(uself.playlist_urll),
                        segment_url,
                    )

                tasks.append(self.download_segment(session, segment_url, i, temp_dir))

            # Запускаем все задачи одновременно
            await asyncio.gather(*tasks)

        # Объединение всех сегментов в один файл
        print("Объединение всех сегментов в один файл")
        with open(video_path, "wb") as f_out:
            for i in range(len(segments)):
                segment_path = os.path.join(temp_dir, f"segment_{i}.ts")
                print(f"{segment_path = }")
                if os.path.exists(segment_path):
                    with open(segment_path, "rb") as f_in:
                        f_out.write(f_in.read())

        # Удаление временных файлов сегментов вместе с папкой
        shutil.rmtree(temp_dir)

        print(f"Скачивание завершено. Видео сохранено в файл: {output_file}")

    def run_async(self) -> None:
        asyncio.run(self.download_hls_playlist())
