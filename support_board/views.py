from django.shortcuts import render
from django.conf import settings
import json
from pathlib import Path


def index(request):
    """Serve the React SPA"""
    manifest_path = Path(settings.BASE_DIR) / 'support_board' / 'static' / 'support_board' / '.vite' / 'manifest.json'

    js_file = None
    css_file = None

    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
            entry = manifest.get('src/main.jsx', {})
            js_file = entry.get('file')
            css_files = entry.get('css', [])
            css_file = css_files[0] if css_files else None

    context = {
        'js_file': js_file,
        'css_file': css_file,
    }
    return render(request, 'support_board/index.html', context)
