import asyncio
from agents import create_fina_sync_agent
from google.adk.runners import InMemoryRunner

async def run_pipeline(file_path):
    print(f"📂 New file detected: {file_path}")
    print("🤖 Initializing Dispatcher Agent Runner...")

    # 1. Initialize the Runner with a FRESH agent instance
    agent_instance = create_fina_sync_agent()
    runner = InMemoryRunner(agent=agent_instance)
    
    # 2. Construct the user prompt
    prompt = f"I have a new file for you to process. The file path is: '{file_path}'. Please analyze it."
    
    try:
        print("\n----- 🟢 STARTING AGENT TRACE -----")
        # 3. Use run_debug to execute the agent
        await runner.run_debug(prompt)
        print("----- 🏁 AGENT EXECUTION COMPLETE -----")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")

if __name__ == "__main__":
    # Simulate an Expense File Trigger (CSV)
    from utils import get_data_file_path
    dummy_file = get_data_file_path("expenses_feb.csv")
    
    asyncio.run(run_pipeline(dummy_file))