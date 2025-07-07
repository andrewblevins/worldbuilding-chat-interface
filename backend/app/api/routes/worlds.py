"""
Worlds API routes for the Worldbuilding Chat Interface.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path

router = APIRouter()


class WorldInfo(BaseModel):
    """World information model."""
    name: str
    path: str
    created_at: str
    size: int
    entry_count: int


@router.get("/list", response_model=List[WorldInfo])
async def list_worlds():
    """List all available worlds."""
    # TODO: Implement world discovery
    return []


@router.get("/{world_name}/files")
async def get_world_files(world_name: str):
    """Get file structure for a specific world."""
    # TODO: Implement world file listing
    return {
        "world_name": world_name,
        "files": []
    }


@router.get("/{world_name}/overview")
async def get_world_overview(world_name: str):
    """Get world overview information."""
    # TODO: Implement world overview
    return {
        "world_name": world_name,
        "overview": "World overview not implemented yet"
    } 