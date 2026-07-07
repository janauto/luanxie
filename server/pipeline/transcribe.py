"""mlx-whisper 本地转写。模型懒加载单例(首次调用会下载 ~1.6GB)。"""
import asyncio

from .. import config

WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"

_lock = asyncio.Lock()


def _transcribe_sync(audio_path: str) -> str:
    import mlx_whisper  # 懒导入:未安装时不影响文字/图片链路

    result = mlx_whisper.transcribe(audio_path, path_or_hf_repo=WHISPER_MODEL)
    return result["text"].strip()


async def transcribe(media_path: str) -> str:
    path = str(config.DATA_DIR / media_path)
    async with _lock:  # 模型非线程安全,串行执行
        return await asyncio.to_thread(_transcribe_sync, path)
