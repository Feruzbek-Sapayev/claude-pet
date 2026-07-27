#!/bin/bash
# Claude desktop pet -- o'chirish.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 topilmadi -- qo'lda o'chirish yo'riqnomasi README.md da."
    read -r -p "Davom etish uchun Enter..."
    exit 1
fi

python3 uninstall.py
echo
read -r -p "Davom etish uchun Enter..."
