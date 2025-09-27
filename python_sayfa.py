"""Basit özgeçmiş (CV) depolama aracı.

Bu betik, komut satırından girilen CV bilgilerini yerel bir JSON dosyasında
saklar. İhtiyaca göre yeni kayıt ekleyebilir, kayıtları listeleyebilir veya ada
göre arama yapabilirsiniz.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional


STORAGE_PATH = Path("cv_kayitlari.json")


@dataclass
class CVEntry:
    """Bir adayın CV bilgilerini temsil eder."""

    name: str
    email: str
    phone: str
    skills: List[str]
    experience: str
    education: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "CVEntry":
        """Sözlük verisinden güvenli bir şekilde :class:`CVEntry` üretir."""

        skills = data.get("skills", [])
        if isinstance(skills, str):
            skills = [item.strip() for item in skills.split(",") if item.strip()]
        elif isinstance(skills, Iterable):
            skills = [str(item).strip() for item in skills if str(item).strip()]
        else:
            skills = []

        return cls(
            name=str(data.get("name", "Bilinmiyor")),
            email=str(data.get("email", "")),
            phone=str(data.get("phone", "")),
            skills=skills,
            experience=str(data.get("experience", "")),
            education=str(data.get("education", "")),
            timestamp=str(data.get("timestamp", datetime.now().isoformat(timespec="seconds"))),
        )


class CVStorage:
    """CV kayıtlarını yerel bir JSON dosyasında saklar."""

    def __init__(self, path: Path = STORAGE_PATH) -> None:
        self.path = path
        self._entries: List[CVEntry] = []
        self._load()

    @property
    def entries(self) -> List[CVEntry]:
        return list(self._entries)

    def _load(self) -> None:
        if not self.path.exists():
            self._entries = []
            return

        try:
            raw_data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raw_data = []

        self._entries = [CVEntry.from_dict(item) for item in raw_data]

    def _save(self) -> None:
        serialized = [asdict(entry) for entry in self._entries]
        self.path.write_text(json.dumps(serialized, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_entry(self, entry: CVEntry) -> None:
        self._entries.append(entry)
        self._save()

    def find_by_name(self, keyword: str) -> List[CVEntry]:
        keyword_lower = keyword.lower()
        return [entry for entry in self._entries if keyword_lower in entry.name.lower()]


def prompt_cv_entry() -> CVEntry:
    """Kullanıcıdan CV bilgilerini ister ve :class:`CVEntry` döndürür."""

    print("Yeni bir CV kaydı oluşturuluyor. Çıkmak için Ctrl+C.")
    name = input("Ad Soyad: ").strip()
    email = input("E-posta: ").strip()
    phone = input("Telefon: ").strip()
    skills_raw = input("Yetenekler (virgülle ayırın): ")
    experience = input("Deneyim özetiniz: ")
    education = input("Eğitim bilgileri: ")

    skills = [skill.strip() for skill in skills_raw.split(",") if skill.strip()]
    timestamp = datetime.now().isoformat(timespec="seconds")

    return CVEntry(
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        experience=experience,
        education=education,
        timestamp=timestamp,
    )


def format_entry(entry: CVEntry) -> str:
    """CV kaydını kullanıcı dostu bir metne dönüştürür."""

    skills = ", ".join(entry.skills) if entry.skills else "Belirtilmemiş"
    return (
        f"Ad Soyad : {entry.name}\n"
        f"E-posta  : {entry.email}\n"
        f"Telefon  : {entry.phone}\n"
        f"Yetenekler: {skills}\n"
        f"Deneyim  : {entry.experience}\n"
        f"Eğitim   : {entry.education}\n"
        f"Kaydedildi: {entry.timestamp}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CV kayıtlarını yönetir.")
    parser.add_argument(
        "--dosya",
        type=Path,
        default=STORAGE_PATH,
        help="Kayıtların saklanacağı JSON dosyası.",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("liste", help="Tüm kayıtları listeler.")

    ara_parser = subparsers.add_parser("ara", help="Ada göre arama yapar.")
    ara_parser.add_argument("anahtar", help="Aramak istediğiniz ad veya kelime.")

    ekle_parser = subparsers.add_parser("ekle", help="Yeni kayıt ekler.")
    ekle_parser.add_argument("--ad", required=False, help="Ad Soyad bilgisi.")
    ekle_parser.add_argument("--email", required=False, help="E-posta adresi.")
    ekle_parser.add_argument("--telefon", required=False, help="Telefon numarası.")
    ekle_parser.add_argument("--yetenek", action="append", help="Yetenek ekler. Çoklu kullanım mümkündür.")
    ekle_parser.add_argument("--deneyim", required=False, help="Deneyim özeti.")
    ekle_parser.add_argument("--egitim", required=False, help="Eğitim bilgileri.")

    return parser.parse_args()


def collect_entry_from_args(args: argparse.Namespace) -> CVEntry:
    """Argümanlardan bir CV kaydı oluşturur, eksik bilgi varsa kullanıcıdan ister."""

    def ensure(value: Optional[str], prompt: str) -> str:
        if value:
            return value.strip()
        return input(prompt).strip()

    name = ensure(args.ad, "Ad Soyad: ")
    email = ensure(args.email, "E-posta: ")
    phone = ensure(args.telefon, "Telefon: ")

    skills: List[str]
    if args.yetenek:
        skills = [item.strip() for item in args.yetenek if item.strip()]
    else:
        skills_raw = input("Yetenekler (virgülle ayırın): ")
        skills = [item.strip() for item in skills_raw.split(",") if item.strip()]

    experience = ensure(args.deneyim, "Deneyim özetiniz: ")
    education = ensure(args.egitim, "Eğitim bilgileri: ")

    return CVEntry(
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        experience=experience,
        education=education,
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )


def main() -> None:
    args = parse_args()
    storage = CVStorage(args.dosya)

    if args.command == "liste":
        if not storage.entries:
            print("Henüz kayıt yok.")
            return
        for index, entry in enumerate(storage.entries, start=1):
            print(f"--- Kayıt #{index} ---")
            print(format_entry(entry))
        return

    if args.command == "ara":
        results = storage.find_by_name(args.anahtar)
        if not results:
            print(f"'{args.anahtar}' için kayıt bulunamadı.")
            return
        for entry in results:
            print(format_entry(entry))
        return

    if args.command == "ekle":
        entry = collect_entry_from_args(args)
        storage.add_entry(entry)
        print(f"{entry.name} kaydedildi.")
        return

    # Komut verilmediyse interaktif mod çalışsın.
    try:
        entry = prompt_cv_entry()
    except KeyboardInterrupt:
        print("\nİşlem iptal edildi.")
        return

    storage.add_entry(entry)
    print(f"{entry.name} kaydedildi. Toplam kayıt sayısı: {len(storage.entries)}")


if __name__ == "__main__":
    main()

