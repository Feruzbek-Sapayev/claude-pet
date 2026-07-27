#!/bin/bash
# Claude desktop pet -- o'rnatish. Shu faylni Finder'da ikki marta bosing.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo
    echo "Python 3 topilmadi."
    echo "https://python.org saytidan Python 3.8 yoki undan yangisini o'rnating."
    echo
    read -r -p "Davom etish uchun Enter..."
    exit 1
fi

chmod +x start-pet.command uninstall.command 2>/dev/null
python3 install.py
echo
read -r -p "Davom etish uchun Enter..."
