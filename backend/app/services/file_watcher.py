"""
File watcher service for monitoring world files in real-time.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
from loguru import logger


class WorldFileHandler(FileSystemEventHandler):
    """Handler for world file system events."""
    
    def __init__(self, callback=None):
        self.callback = callback
        
    def on_modified(self, event):
        if not event.is_directory:
            logger.debug(f"File modified: {event.src_path}")
            if self.callback:
                asyncio.create_task(self.callback('modified', event.src_path))
    
    def on_created(self, event):
        if not event.is_directory:
            logger.debug(f"File created: {event.src_path}")
            if self.callback:
                asyncio.create_task(self.callback('created', event.src_path))
    
    def on_deleted(self, event):
        if not event.is_directory:
            logger.debug(f"File deleted: {event.src_path}")
            if self.callback:
                asyncio.create_task(self.callback('deleted', event.src_path))


class FileWatcher:
    """File watcher service for monitoring world file changes."""
    
    def __init__(self, watch_dir: str = "worlds"):
        self.watch_dir = Path(watch_dir)
        self.observer: Optional[Observer] = None
        self.handler: Optional[WorldFileHandler] = None
        self._running = False
        
    @property
    def running(self) -> bool:
        """Check if file watcher is running."""
        return self._running and self.observer is not None and self.observer.is_alive()
        
    def start(self, callback=None):
        """Start the file watcher."""
        if self.running:
            logger.warning("File watcher is already running")
            return
            
        # Ensure watch directory exists
        self.watch_dir.mkdir(exist_ok=True)
        
        # Create handler and observer
        self.handler = WorldFileHandler(callback)
        self.observer = Observer()
        
        # Start watching
        self.observer.schedule(self.handler, str(self.watch_dir), recursive=True)
        self.observer.start()
        self._running = True
        
        logger.info(f"File watcher started monitoring: {self.watch_dir}")
        
    def stop(self):
        """Stop the file watcher."""
        if not self.running:
            logger.warning("File watcher is not running")
            return
            
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            
        self.handler = None
        self._running = False
        
        logger.info("File watcher stopped")


# Create singleton instance
file_watcher = FileWatcher() 