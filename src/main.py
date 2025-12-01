import asyncio
from agents import create_fina_sync_agent
# Import the Database Session Service for persistence
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types

async def run_pipeline(file_path):
    print(f"📂 New file detected: {file_path}")
    
    # 1. Setup Persistent Session Database
    # We use 'sqlite+aiosqlite:///' to tell SQLAlchemy to use the async driver
    db_url = "sqlite+aiosqlite:///fina_sync.db"
    
    # Initialize the service with the async URL
    session_service = DatabaseSessionService(db_url=db_url)
    
    # 2. Create the Agent
    pipeline_agent = create_fina_sync_agent()
    
    # 3. Initialize Runner with the Session Service
    runner = Runner(
        agent=pipeline_agent, 
        app_name="FinaSyncApp",
        session_service=session_service
    )
    
    session_id = "monthly_finance_session"
    
    # 4. Create User Message
    # We append a direct instruction to force the update
    prompt_text = f"I have a new file: '{file_path}'. Process it, update the cache, and RE-GENERATE the chart and report immediately using available data."
    user_msg = types.Content(role="user", parts=[types.Part(text=prompt_text)])

    print("\n----- 🟢 STARTING PIPELINE (Persistent Session) -----")
    
    # 5. Run the Agent
    try:
        # FIX: Handle None return from get_session instead of relying on try/except
        session = await session_service.get_session(
            app_name="FinaSyncApp", 
            user_id="user_default", 
            session_id=session_id
        )

        if session is None:
            print(f"📝 Creating new session: {session_id}")
            session = await session_service.create_session(
                app_name="FinaSyncApp", 
                user_id="user_default", 
                session_id=session_id
            )
        else:
            print(f"📖 Resumed existing session: {session_id}")

        async for event in runner.run_async(
            user_id="user_default",
            session_id=session.id,
            new_message=user_msg
        ):
            # Print the agent's output as it streams
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(f"🤖 Agent: {text}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

    print("----- 🏁 PIPELINE COMPLETE -----")

if __name__ == "__main__":
    # Simulate an Expense File Trigger
    dummy_file = "test_data/expenses_feb.csv" 
    asyncio.run(run_pipeline(dummy_file))