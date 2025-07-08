#!/usr/bin/env python3
"""
Development server runner with auto-reload.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        reload_excludes=["*.pyc", "__pycache__", "*.log", "venv", ".git"],
        reload_delay=0.25,  # Faster reload detection
        log_level="info",
        access_log=True,
        use_colors=True,
        factory=False,  # Ensures fresh imports on reload
        loop="auto"
    ) 