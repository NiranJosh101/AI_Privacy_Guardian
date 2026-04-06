from pydantic import BaseModel, Field

class PolicyRequest(BaseModel):
    domain: str = Field(..., example="google.com")
    raw_text: str = Field(..., description="The full scraped text of the privacy policy")