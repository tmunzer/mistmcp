from enum import Enum
import uuid
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from ...__main import mcp
import os
from pathlib import Path
import mistapi


class User(BaseModel):
    username: str
    email: str = Field(description="User's email address")
    age: int | None = None
    is_active: bool = True
    
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


# Asynchronous tool (ideal for I/O-bound operations)
@mcp.tool(
    name="find_products",           # Custom tool name for the LLM
    description="Search the product catalog with optional category filtering.", # Custom description
    tags={"catalog", "search"},      # Optional tags for organization/filtering
        annotations={
        "title": "Calculate Sum",
        "readOnlyHint": True,   # 	Indicates if the tool only reads without making changes
        "destructiveHint": False, # For non-readonly tools, signals if changes are destructive
        "idempotentHint": True, # Indicates if repeated identical calls have the same effect as a single call
        "openWorldHint": True # Specifies if the tool interacts with external systems
    }
)
async def search_products(
    # Numbers with range constraints
    count: Annotated[int, Field(ge=0, le=100, default=4)],         # 0 <= count <= 100
    ratio: Annotated[float, Field(gt=0, lt=1.0, )],       # 0 < ratio < 1.0
    
    # String with pattern and length constraints
    user_id: Annotated[str, Field(
        pattern=r"^[A-Z]{2}\d{4}$",                     # Must match regex pattern
        description="User ID in format XX0000"
    )],
    
    # String with length constraints
    comment: Annotated[str, Field(min_length=3, max_length=500)] = "",
    
    # Numeric constraints
    factor: Annotated[int, Field(multiple_of=5)] = 10,  # Must be multiple of 5
    user: User,
    item_id: uuid.UUID,  # String UUID or UUID object
    query: str,                   # Required - no default value
    max_results: int = 10,        # Optional - has default value
    sort_by: str = "relevance",   # Optional - has default value
    category: str | None = None,   # Optional - can be None
    color_filter: Color = Color.RED
) -> list[dict]:
    """Search the product catalog."""
    # Implementation...
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/weather/{city}") as response:
            # Check response status before returning
            response.raise_for_status()
            if b == 0:
                # Error messages from ToolError are always sent to clients,
                # regardless of mask_error_details setting
                raise ToolError("Division by zero is not allowed.")
            
            # If mask_error_details=True, this message would be masked
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError("Both arguments must be numbers.")
            return await response.json()

def create_env_file():
    """Create the environment file with Mist API credentials"""
    env_file = os.path.expanduser("~/.mist_env_ld_ro")
    
    # Get user input for credentials
    host = input("Enter Mist host (e.g. api.mist.com): ")
    api_token = input("Enter your API token: ")
    
    # Create the env file content
    env_content = f"""
host={host}
apitoken={api_token}
"""
    
    # Write to file
    Path(env_file).write_text(env_content.strip())
    print(f"Environment file created at {env_file}")

def test_connection():
    """Test the API connection"""
    try:
        session = mistapi.APISession(env_file="~/.mist_env_ld_ro")
        session.login()
        print("Successfully connected to Mist API!")
    except Exception as e:
        print(f"Error connecting to Mist API: {e}")

if __name__ == "__main__":
    create_env_file()
    test_connection()

