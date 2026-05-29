from app.brain.planner import Planner
from app.agents.website_agent import WebsiteAgent


class Orchestrator:

    def __init__(self):

        self.planner = Planner()

        self.website_agent = WebsiteAgent()

    def execute(self, user_request):

        plan = self.planner.create_plan(
            user_request
        )

        print(plan)

        if plan["agent"] == "website":

            return self.website_agent.execute(
                user_request
            )

        raise Exception(
            "No suitable agent found"
        )