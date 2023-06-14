import json
import os
import struct
import time
from typing import Any, Callable
import vosk

from vosk import SetLogLevel
from pvrecorder import PvRecorder

from modules.Utils.Logger import Logger
from modules.Utils.wtnr.extractor import NumberExtractor


class VoiceRecog:
    model_name: str = "vosk-model-small-ru-0.22-v1"
    samplerate: int = 16000
    frame_length: int = 512
    recorder_delay: int = 15

    def __init__(self) -> None:
        SetLogLevel(-1)
        self.model_path: str = os.path.realpath("modules/VoiceRecog/models/" + self.model_name)
        self.device = int(os.environ.get("MICROPHONE_INDEX"))  # type: ignore
        self.model = vosk.Model(self.model_path)
        self.kaldi_rec = vosk.KaldiRecognizer(self.model, self.samplerate)
        self.recorder = PvRecorder(device_index=self.device, frame_length=self.frame_length)

        Logger.info(f"Loaded model: {self.model_name}")
        Logger.info(f"Using device: {self.recorder.selected_device}")
        Logger.info(f"Samplerate: {self.samplerate}")
        Logger.info(f"Frame length: {self.frame_length}")
        Logger.info(f"Recorder delay: {self.recorder_delay}")

    def __transform_text(self, text: str) -> str:
        extractor = NumberExtractor()
        text = text.capitalize()

        wtn_text = extractor.replace_groups(text)
        if wtn_text is not None:
            text = wtn_text

        Logger.debug(f"Transformed text '{text}'")

        return text

    def recognize(self, callback: Callable[[str], Any]) -> None:
        self.recorder.start()
        ltc = time.time()
        while time.time() - ltc <= self.recorder_delay:
            pcm = self.recorder.read()
            sp = struct.pack("h" * len(pcm), *pcm)

            if self.kaldi_rec.AcceptWaveform(sp):
                r = self.kaldi_rec.Result()
                text: str = json.loads(r)["text"]
                print(r)
                if text:
                    Logger.debug(f"Recognized text '{text}'")
                    ltc = time.time()
                    callback(self.__transform_text(text))
                break
        self.recorder.stop()
