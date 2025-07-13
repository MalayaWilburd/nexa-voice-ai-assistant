from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google 
from prompt import agent_instruction, session_instruction   # importing the agent and session instructions from our prompt file
from tools import get_weather, search_web, send_email  # importing the tools we defined in tools.py
load_dotenv()   # loading environment variables from .env file to have access to the API keys and other configurations


# defining the Assistant class that inherits from Agent
# this class will use the agent_instruction defined in the prompt file to guide its behavior
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=agent_instruction,
            llm=google.beta.realtime.RealtimeModel( #this is the LLM that will be used for the agent
            voice="Charon",
            temperature=0.8 #randomness value, higher value = more randomness
        ),
            tools=[get_weather, search_web, send_email],  # registering the tools we defined in tools.py
        )

# entry point function that will be called when the agent starts
async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(

    )

# startting the session with the room and agent
    await session.start(
        room=ctx.room,
        agent=Assistant(), # the agent is the Assistant class we defined earlier
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

# we wait until the session is ready to process inputs
    await ctx.connect()

# we generate a reply using the session with the session_instruction defined in the prompt file
    await session.generate_reply(
        instructions=session_instruction
    )

# we define the enry point and use it to run the agent
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))