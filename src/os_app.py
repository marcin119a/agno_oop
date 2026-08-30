"""Serves the FAQ agent via Agno's AgentOS.

AgentOS runs the agent as a local FastAPI server; the hosted control
plane at https://os.agno.com/ connects to that local server (it never
sees your API keys or model calls — only your browser talks to
localhost). Once connected, you get a chat UI plus session/run history
for every request as a replacement for ad-hoc console logging.

Usage:
    faq-agent-os                 # starts the server on http://localhost:7777
    python -m os_app             # equivalent

Then open https://os.agno.com/, and add http://localhost:7777 as a new OS.
"""

from __future__ import annotations

import sys

from agno.db.sqlite import SqliteDb
from agno.os import AgentOS

from agents.faq.agent import create_faq_agent
from config import Settings
from handoff import create_handoff_workflow
from agents.human.agent import create_human_agent
from agents.triage.agent import create_triage_agent
from support_team import create_support_team

settings = Settings()
# A persistent db (rather than the CLI's ephemeral InMemoryDb) so sessions,
# metrics and traces survive restarts, and AgentOS control-plane features
# like Service Accounts (which need a real db) work.
db = SqliteDb(db_file="faq_agent_os.db")
agent = create_faq_agent(settings, db=db)
triage_agent = create_triage_agent(settings, db=db)
handoff_workflow = create_handoff_workflow(
    settings,
    db=db,
    triage_agent=triage_agent,
    faq_agent=agent,
)
human_agent = create_human_agent(settings, db=db)
support_team = create_support_team(settings, db=db, faq_agent=agent, human_agent=human_agent)

agent_os = AgentOS(
    name="faq-agent",
    agents=[agent, triage_agent],
    teams=[support_team],
    workflows=[handoff_workflow],
    db=db,
)
app = agent_os.get_app()


def main() -> None:
    if not settings.openai_api_key:
        sys.exit(
            "Missing API key. Set OPENAI_API_KEY in the .env file in the working directory\n"
            "(or set the OPENAI_API_KEY environment variable)."
        )
    agent_os.serve(app="os_app:app", reload=True)


if __name__ == "__main__":
    main()
