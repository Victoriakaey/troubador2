import json

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from intelligent_game_decision_engine.tools.music_generator_tool import MusicGeneratorTool
from intelligent_game_decision_engine.tools.game_action_executor_tool import GameActionExecutorTool


@CrewBase
class IntelligentGameDecisionEngineCrew:
    """IntelligentGameDecisionEngine crew"""

    GAME_DESCRIPTION: str = "first person shooter"
    _strudel_history: list = []

    @before_kickoff
    def inject_internal_inputs(self, inputs):
        inputs["game_description"] = self.GAME_DESCRIPTION
        inputs["current_strudel_code"] = json.dumps(self._strudel_history)
        return inputs

    @after_kickoff
    def capture_strudel_output(self, result):
        try:
            output = json.loads(result.raw)
            tool_response = output.get("tool_invocation", {}).get("tool_response")
            if tool_response:
                self._strudel_history.append(str(tool_response))
        except (json.JSONDecodeError, AttributeError):
            pass
        return result

    @agent
    def intelligent_game_decision_agent(self) -> Agent:
        
        return Agent(
            config=self.agents_config["intelligent_game_decision_agent"],
            
            
            tools=[
                MusicGeneratorTool(),
                GameActionExecutorTool(),
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4.1",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def process_dynamic_game_state_input(self) -> Task:
        return Task(
            config=self.tasks_config["process_dynamic_game_state_input"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the IntelligentGameDecisionEngine crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )


