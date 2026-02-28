from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, Optional, Union
import requests
import json

class GameActionExecutorInput(BaseModel):
    """Input schema for Game Action Executor Tool."""
    api_endpoint: str = Field(
        ..., 
        description="The URL endpoint for the game action API"
    )
    action_payload: str = Field(
        ..., 
        description="JSON string containing the action data to send (e.g., '{\"action\": \"move\", \"direction\": \"north\"}')"
    )
    headers: Optional[Dict[str, str]] = Field(
        default={"Content-Type": "application/json"}, 
        description="Custom headers for the request"
    )
    timeout: Optional[int] = Field(
        default=30, 
        description="Request timeout in seconds"
    )

class GameActionExecutorTool(BaseTool):
    """Tool for executing game actions via HTTP POST requests to game APIs."""

    name: str = "game_action_executor_tool"
    description: str = (
        "Executes game actions by making HTTP POST requests to game API endpoints. "
        "Takes a JSON string as action_payload parameter. "
        "Handles various response codes and network errors gracefully, returning "
        "structured responses with success status, response data, error messages, and HTTP status codes."
    )
    args_schema: Type[BaseModel] = GameActionExecutorInput

    def _run(
        self, 
        api_endpoint: str, 
        action_payload: str, 
        headers: Optional[Dict[str, str]] = None, 
        timeout: Optional[int] = None
    ) -> str:
        """
        Execute a game action via HTTP POST request.
        
        Args:
            api_endpoint: The URL endpoint for the game action API
            action_payload: JSON string containing the action data to send
            headers: Custom headers for the request
            timeout: Request timeout in seconds
            
        Returns:
            JSON string with structured response containing success status, 
            response data, error message, and status code
        """
        # Set default values if not provided
        if headers is None:
            headers = {"Content-Type": "application/json"}
        if timeout is None:
            timeout = 30

        # Initialize response structure
        response_structure = {
            "success": False,
            "response_data": None,
            "error_message": None,
            "status_code": None
        }

        try:
            # Validate the endpoint URL
            if not api_endpoint or not isinstance(api_endpoint, str):
                response_structure["error_message"] = "Invalid API endpoint provided"
                return json.dumps(response_structure, indent=2)

            # Parse and validate the action payload JSON string
            try:
                if isinstance(action_payload, str):
                    action_data = json.loads(action_payload)
                else:
                    response_structure["error_message"] = "Action payload must be a JSON string"
                    return json.dumps(response_structure, indent=2)
            except json.JSONDecodeError as e:
                response_structure["error_message"] = f"Invalid JSON in action_payload: {str(e)}"
                return json.dumps(response_structure, indent=2)

            # Make the POST request
            response = requests.post(
                url=api_endpoint,
                json=action_data,
                headers=headers,
                timeout=timeout
            )

            # Store the status code
            response_structure["status_code"] = response.status_code

            # Handle different HTTP response codes
            if 200 <= response.status_code <= 299:
                # Success responses
                response_structure["success"] = True
                try:
                    # Try to parse JSON response
                    response_structure["response_data"] = response.json()
                except json.JSONDecodeError:
                    # If response is not JSON, store as text
                    response_structure["response_data"] = response.text
                
                return json.dumps(response_structure, indent=2)

            elif 400 <= response.status_code <= 499:
                # Client error responses
                response_structure["error_message"] = f"Client error (HTTP {response.status_code})"
                try:
                    error_details = response.json()
                    response_structure["response_data"] = error_details
                    if "message" in error_details:
                        response_structure["error_message"] += f": {error_details['message']}"
                    elif "error" in error_details:
                        response_structure["error_message"] += f": {error_details['error']}"
                except json.JSONDecodeError:
                    response_structure["error_message"] += f": {response.text}"
                
                return json.dumps(response_structure, indent=2)

            elif 500 <= response.status_code <= 599:
                # Server error responses
                response_structure["error_message"] = f"Server error (HTTP {response.status_code})"
                try:
                    error_details = response.json()
                    response_structure["response_data"] = error_details
                    if "message" in error_details:
                        response_structure["error_message"] += f": {error_details['message']}"
                    elif "error" in error_details:
                        response_structure["error_message"] += f": {error_details['error']}"
                except json.JSONDecodeError:
                    response_structure["error_message"] += f": {response.text}"
                
                return json.dumps(response_structure, indent=2)

            else:
                # Unexpected status codes
                response_structure["error_message"] = f"Unexpected HTTP status code: {response.status_code}"
                try:
                    response_structure["response_data"] = response.json()
                except json.JSONDecodeError:
                    response_structure["response_data"] = response.text
                
                return json.dumps(response_structure, indent=2)

        except requests.exceptions.ConnectionError as e:
            # Connection errors
            response_structure["error_message"] = f"Connection error: Unable to connect to {api_endpoint}. {str(e)}"
            return json.dumps(response_structure, indent=2)

        except requests.exceptions.Timeout as e:
            # Timeout errors
            response_structure["error_message"] = f"Request timeout: The request to {api_endpoint} timed out after {timeout} seconds. {str(e)}"
            return json.dumps(response_structure, indent=2)

        except requests.exceptions.RequestException as e:
            # Other request-related errors
            response_structure["error_message"] = f"Request error: {str(e)}"
            return json.dumps(response_structure, indent=2)

        except Exception as e:
            # Catch any other unexpected errors
            response_structure["error_message"] = f"Unexpected error: {str(e)}"
            return json.dumps(response_structure, indent=2)