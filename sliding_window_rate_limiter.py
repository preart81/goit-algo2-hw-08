"""
Реалізація Rate Limiter з використанням алгоритму Sliding Window для обмеження частоти повідомлень у чаті
"""

import random
import time
from collections import deque
from typing import Dict


class SlidingWindowRateLimiter:
    """
    Клас для реалізації алгоритму Sliding Window для точного контролю часових інтервалів.

    Args:
        window_size (int): Розмір вікна (в секундах). (default=10)
        max_requests (int): Максимальна кількість повідомлень у вікні. (default=1)

    Attributes:
        window_size (int): Розмір вікна (в секундах).
        max_requests (int): Максимальна кількість повідомлень у вікні.
        history (Dict[str, deque]): Історія повідомлень користувачів.
    """

    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.history: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Очищає вікно застарілих повідомлень та оновлює активне часове вікно.

        1.Перевіряє, чи існує історія повідомлень користувача.
        2.Видаляє застарілі повідомлення з історії користувача.
        3. При видаленні всіх повідомлень з вікна користувача видаляє запис про нього з історії.

        Args:
            user_id (str): ID користувача.
            current_time (float): Поточний час в секундах.
        """
        if user_id in self.history:
            while self.history[user_id] and self.history[user_id][0] < current_time - self.window_size:
                self.history[user_id].popleft()
        
        if not self.history[user_id]:
            del self.history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє можливість відправлення повідомлення користувачу в поточному часовому вікні.

        1.Очищає вікно застарілих повідомлень та оновлює активне часове вікно.
        2.Перевіряє можливість відправлення повідомлення користувачу в поточному часовому вікні.

        Args:
            user_id (str): ID користувача.

        Returns:
            bool: True, якщо можна відправити повідомлення, False в іншому випадку.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id in self.history:
            return len(self.history[user_id]) < self.max_requests
        return True

    def record_message(self, user_id: str) -> bool:
        """
        Записує повідомлення користувача та оновлює історію.

        1.Перевіряє можливість відправлення повідомлення користувачу в поточному часовому вікні.
        2.Записує повідомлення користувача в історію.

        Args:
            user_id (str): ID користувача.

        Returns:
            bool: True, якщо повідомлення успішно записано, False в іншому випадку.
        """
        current_time = time.time()
        if self.can_send_message(user_id):
            if user_id not in self.history:
                self.history[user_id] = deque()
            self.history[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Розраховує час очікування до можливості відправлення наступного повідомлення.

        1. Очищає вікно застарілих повідомлень та оновлює активне часове вікно.
        2. Розраховує час очікування до можливості відправлення наступного повідомлення.

        Args:
            user_id (str): ID користувача.

        Returns:
            float: Час очікування в секундах.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id in self.history:
            return max(0, self.window_size - (current_time - self.history[user_id][-1]))
        return 0


# Демонстрація роботи
def test_rate_limiter():
    """
    Тестова функція.
    """
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
