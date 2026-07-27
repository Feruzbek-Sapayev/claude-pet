#!/bin/bash
# Claude desktop pet -- macOS uchun ishga tushirgich.
# Papka qayerda bo'lsa ham ishlaydi.
cd "$(dirname "$0")" || exit 1

# Tkinter framework qurilmasida bo'lishi kerak, shuning uchun python3 qidiramiz
for PY in python3 /usr/local/bin/python3 /opt/homebrew/bin/python3 \
          /Library/Frameworks/Python.framework/Versions/Current/bin/python3; do
    if command -v "$PY" >/dev/null 2>&1; then
        exec "$PY" pet.py "$@"
    fi
done

echo "Python 3 topilmadi. https://python.org saytidan o'rnating."
read -r -p "Davom etish uchun Enter..."
exit 1
