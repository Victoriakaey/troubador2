import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from intelligent_game_decision_engine.tools.game_action_executor_tool import GameActionExecutorTool




@CrewBase
class IntelligentGameDecisionEngineCrew:
    """IntelligentGameDecisionEngine crew"""

    
    @agent
    def intelligent_game_decision_agent(self) -> Agent:
        
        return Agent(
            config=self.agents_config["intelligent_game_decision_agent"],
            
            
            tools=[				GameActionExecutorTool()],
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


