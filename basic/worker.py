import uuid

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware.middleware import Middleware

from stable_diffusion_with_fastapi.basic.text_to_image import TextToImage


class TextToImageMiddleware(Middleware):
    '''
    bear an instance of TextTOImage, the image generation service. 
    "after_process_boot" allow us to plug our own logic.we tell it to load the stable 
    diffusion model when the worker process has booted up. 
    
    '''
    def __init__(self) -> None:
        super().__init__()
        self.text_to_image = TextToImage()

    def after_process_boot(self, broker):
        self.text_to_image.load_model()
        return super().after_process_boot(broker)


text_to_image_middleware = TextToImageMiddleware()
redis_broker = RedisBroker(host="localhost")
redis_broker.add_middleware(text_to_image_middleware)
dramatiq.set_broker(redis_broker)


@dramatiq.actor()
def text_to_image_task(
    prompt: str, *, negativa_prompt: str | None = None, num_steps: int = 50
):
    image = text_to_image_middleware.text_to_image.generate(
        prompt, negative_prompt=negativa_prompt, num_steps=num_steps
    )
    image.save(f"{uuid.uuid()}.png")
