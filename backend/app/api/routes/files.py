"""
Files API routes for the Worldbuilding Chat Interface.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()


class FileInfo(BaseModel):
    """File information model."""
    name: str
    path: str
    size: int
    modified: str
    type: str


@router.get("/list", response_model=List[FileInfo])
async def list_files(world_path: str = None):
    """List files in a world directory."""
    # TODO: Implement file listing
    return []


@router.get("/read")
async def read_file(file_path: str):
    """Read a specific file."""
    # TODO: Implement file reading
    return {
        "path": file_path,
        "content": "File content not implemented yet"
    } 