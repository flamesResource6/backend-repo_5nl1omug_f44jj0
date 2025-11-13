"""
Database Schemas for Presentation Builder & Tool Finder

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

# ----------------------------
# Presentation & Slides
# ----------------------------
class Slide(BaseModel):
    heading: str = Field(..., description="Slide heading/title")
    content: str = Field("", description="Main text content of the slide")
    notes: Optional[str] = Field(None, description="Presenter notes")

class Presentation(BaseModel):
    title: str = Field(..., description="Presentation title")
    description: Optional[str] = Field(None, description="Short description")
    slides: List[Slide] = Field(default_factory=list, description="Ordered list of slides")
    tags: List[str] = Field(default_factory=list, description="Tags for search")

# ----------------------------
# Tool Directory
# ----------------------------
class Tool(BaseModel):
    name: str = Field(..., description="Tool name")
    url: HttpUrl = Field(..., description="Official website or landing page")
    category: str = Field(..., description="Category like design, writing, dev, ai, etc.")
    description: str = Field("", description="What the tool does")
    tags: List[str] = Field(default_factory=list, description="Keywords for search")
    is_free: bool = Field(True, description="Whether a free plan exists")
