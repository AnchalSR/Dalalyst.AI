from services.video_service import VideoEngineService


class VideoAgent:
    def __init__(self):
        self.service = VideoEngineService()

    def generate(self, symbol: str) -> dict:
        return self.service.generate_script(symbol)
