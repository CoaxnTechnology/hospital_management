#!/bin/bash

echo "🔎 Wrapping plain <label>Text</label> with {% trans %}..."

find . -type f -name "*.html" | while read file; do

  # Wrap plain label text (no {{ }} and no trans already)
  sed -i -E '
    s#<label>([[:space:]]*)([^<{][^<{]*)</label>#<label>\1{% trans "\2" %}</label>#g
    ' "$file"

done

echo "✅ Done."
echo "⚠️  Now run: python manage.py makemessages -a"
