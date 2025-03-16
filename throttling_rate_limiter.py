"""
Реалізація Rate Limiter з використанням алгоритму Throttling для обмеження частоти повідомлень у чаті
"""

import random
import time
from typing import Dict


class ThrottlingRateLimiter:
    """
    Rate Limiter з використанням алгоритму Throttling для обмеження частоти повідомлень у чаті
    Args:
        min_interval (float): Мінімальний інтервал часу (в секундах) між надсиланням повідомлень від користувача.
    Attributes:
        min_interval (float): Мінімальний інтервал часу (в секундах) між надсиланням повідомлень від користувача.
        history (Dict[str, float]): Історія повідомлень користувача.
    """

    def __init__(self, min_interval: float = 10.0):
        """
        Ініціалізує ThrottlingRateLimiter.
        """
        self.min_interval = min_interval
        self.history: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє можливість відправлення повідомлення користувачу в поточному часовому вікні.

        Args:
            user_id (str): ID користувача.

        Returns:
            bool: True, якщо можна відправити повідомлення, False в іншому випадку.
        """
        if user_id in self.history:
            last_message_time = self.history[user_id]
            time_since_last_message = time.time() - last_message_time
            return time_since_last_message >= self.min_interval
        return True

    def record_message(self, user_id: str) -> bool:
        """
        Записує повідомлення користувача та оновлює історію.

        Args:
            user_id (str): ID користувача.

        Returns:
            bool: True, якщо повідомлення успішно записано, False в іншому випадку.
        """
        if self.can_send_message(user_id):
            self.history[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Розраховує час до можливості відправлення наступного повідомлення.

        Args:
            user_id (str): ID користувача.

        Returns:
            float: Час до можливості відправлення наступного повідомлення в секундах.
        """
        if user_id in self.history:
            last_message_time = self.history[user_id]
            time_since_last_message = time.time() - last_message_time
            return max(0.0, self.min_interval - time_since_last_message)
        return 0.0


def test_throttling_limiter():
    """Тестова функція"""
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_throttling_limiter()
