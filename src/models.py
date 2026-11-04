from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["Campaign not found"])


class Call(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    call_id: str
    campaign_id: str
    phone: str
    status: str
    created_at: AwareDatetime


class CallMessage(Call):
    campaign_name: str | None = None
