"""
Basit bir başlangıç dosyası.
Bu dosyada Python kodu yazabilir ve terminalden çalıştırabilirsiniz.

Çalıştırmak için terminalde:
    python3 /workspace/python_sayfa.py
"""

from datetime import datetime


def greet_user(name: str) -> str:
    """Kullanıcıya selam mesajı döndürür."""
    current_time = datetime.now().strftime("%H:%M:%S")
    return f"Merhaba {name}! Saat {current_time}."


if __name__ == "__main__":
    print("Python sayfan hazır. Kendi kodunu aşağıya ekleyebilirsin.\n")
    print(greet_user("Dostum"))
    # Kendi kodunu aşağıya yaz
    # Örnek: print(sum(range(1, 11)))

