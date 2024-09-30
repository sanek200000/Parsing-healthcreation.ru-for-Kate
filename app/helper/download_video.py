import os
import m3u8
import requests


class DownloadHLS:
    def __init__(self, playlist_url: str, path: str) -> None:
        self.path = path
        self.playlist_url = m3u8.load(playlist_url).playlists[-1].uri

        # print(f'Max resolution {main_playlist.playlists[-1].stream_info.resolution}')

    def get_hls_video(self, output_file="output_video.ts") -> str:
        m3u8_obj = m3u8.load(self.playlist_url)
        segments = m3u8_obj.segments

        # segments_path = os.path.join(self.path, "/temp_segments")
        # os.makedirs(segments_path, exist_ok=True)

        video_path = os.path.join(self.path, output_file)
        with open(video_path, "wb") as f_out:
            for i, segment in enumerate(segments):
                segment_url = segment.uri

                # В случае, если сегменты содержат относительные пути, добавляем базовый URL
                if not segment_url.startswith("http"):
                    segment_url = os.path.join(
                        os.path.dirname(self.playlist_url),
                        segment_url,
                    )

                print(f"Скачиваем сегмент {i+1}/{len(segments)}: {segment_url}")
                response = requests.get(segment_url)

                while True:
                    if response.status_code == 200:
                        f_out.write(response.content)
                        break
                    else:
                        print(f"Не удалось скачать сегмент: {segment_url}")

        return f"Скачивание завершено, видео сохранено в файл: {video_path}"
