from pydantic import BaseModel, field_validator
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseModel):
  chromium_arguments: list[str]
  chromium_path: str
  suap_id: str
  suap_password: str
  mcp_server_port: int
  dev_mode: bool

  @field_validator("chromium_arguments", mode="before")
  @classmethod
  def parse_arguments(cls, v):
    if isinstance(v, str):
      return [f"--{argument.strip()}" for argument in v.split(',') if argument.strip()]
    return v

settings = Settings(
  chromium_arguments=os.environ["CHROMIUM_ARGUMENTS"],
  chromium_path=os.environ["CHROMIUM_PATH"],
  suap_id=os.environ["SUAP_ID"],
  suap_password=os.environ["SUAP_PASSWORD"],
  mcp_server_port=os.environ["MCP_SERVER_PORT"],
  dev_mode=os.environ["DEV_MODE"]
)