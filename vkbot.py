import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll


class VKBot:
    """Класс ВК чат-бота."""

    def __init__(self, token):
        self.vk_session = vk_api.VkApi(token=token)

    def vkbot_up(
        self,
    ):
        for event in VkLongPoll(self.vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.vk_session.method(
                    "messages.send",
                    dict(
                        user_id=event.user_id,
                        message=f"Поступило сообщение: {event.text}.",
                        keyboard=None,
                        random_id=0,
                    ),
                )
