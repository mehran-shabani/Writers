from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    job_id: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    error: Optional[str] = None
    md_key: Optional[str] = None
    pdf_key: Optional[str] = None
    md_url: Optional[str] = None
    pdf_url: Optional[str] = None

class SummarizeIn(BaseModel):
    text: str
    language: str = "fa"
    domain: str = "medical"

class Section(BaseModel):
    heading: str
    summary: str
    key_points: List[str]
    traps: List[str]

class MCQ(BaseModel):
    stem: str
    options: List[str]
    answer: str
    rationale: str

class SummarizeOut(BaseModel):
    title: str
    sections: List[Section]
    mcqs: List[MCQ]
    night_before: str
