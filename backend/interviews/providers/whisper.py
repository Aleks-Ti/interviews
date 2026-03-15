import asyncio
import os
import tempfile


class LocalWhisper:
    """Local Whisper transcription via openai-whisper library. No API key required."""

    def __init__(self, model_name: str = "base") -> None:
        self._model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            import whisper
            self._model = whisper.load_model(self._model_name)
        return self._model

    async def transcribe(self, audio: bytes, filename: str = "audio.webm") -> str:
        def _run() -> str:
            import whisper  # noqa: F401 — ensure available
            model = self._get_model()
            suffix = os.path.splitext(filename)[1] or ".webm"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio)
                tmp_path = tmp.name
            try:
                result = model.transcribe(tmp_path)
                return result["text"].strip()
            finally:
                os.unlink(tmp_path)

        return await asyncio.to_thread(_run)


_whisper_instance: LocalWhisper | None = None


def get_local_whisper() -> LocalWhisper:
    global _whisper_instance
    if _whisper_instance is None:
        from interviews.core.configuration import conf
        _whisper_instance = LocalWhisper(model_name=conf.ai.whisper_model)
    return _whisper_instance
