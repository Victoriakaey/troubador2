import json
import requests
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


GAME_DESCRIPTION = "office simulator"


class MusicGeneratorInput(BaseModel):
    """Input schema for Music Generator Tool."""
    game_state: str = Field(
        ...,
        description="The current game state, e.g. 'Player enters a dimly lit dungeon'",
    )


class MusicGeneratorTool(BaseTool):
    """Tool for generating game music via the generate-music API."""

    name: str = "music_generator"
    description: str = (
        "Generates game music by calling the music generation API. "
        "Takes a game_state and returns generated music data."
    )
    args_schema: Type[BaseModel] = MusicGeneratorInput

    def _run(self, game_state: str) -> str:
        try:
            response = requests.post(
                url="https://us-central1-llama-hack.cloudfunctions.net/generate-music",
                json={
                    "game_description": GAME_DESCRIPTION,
                    "game_state": game_state,
                },
                headers={"Content-Type": "application/json"},
                timeout=60,
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return json.dumps({"error": str(e)})
