import os
import pandas as pd
from evidently import Report
from evidently.presets import TextEvals
from evidently.descriptors import TextLength, Contains, Sentiment

LOG_FILE = "agent_logs.csv"

def adk_evidently_logger(callback_context) -> None:
    """Extracts raw text directly from the ADK Context structure."""
    try:
        user_prompt = ""
        agent_response = ""
        
        # 1. Unpack from the formal ADK interaction structure
        if hasattr(callback_context, 'interaction') and callback_context.interaction:
            inter = callback_context.interaction
            
            # Extract User Prompt text from the input parts list
            if hasattr(inter, 'input') and inter.input and hasattr(inter.input, 'parts'):
                parts = [p.text for p in inter.input.parts if hasattr(p, 'text') and p.text]
                user_prompt = " ".join(parts)
                
            # Extract Agent Response text from the output parts list
            if hasattr(inter, 'output') and inter.output and hasattr(inter.output, 'parts'):
                parts = [p.text for p in inter.output.parts if hasattr(p, 'text') and p.text]
                agent_response = " ".join(parts)

        # 2. Check if strings are flat attributes on the root context
        if not user_prompt:
            user_prompt = getattr(callback_context, 'input_text', '')
        if not agent_response:
            agent_response = getattr(callback_context, 'output_text', '')

        # Clean whitespace
        user_prompt = str(user_prompt).strip()
        agent_response = str(agent_response).strip()

        # 3. Validation: Catch extraction failures immediately
        if not user_prompt or not agent_response:
            print(f"\n⚠️ [Telemetry Warning] Incomplete extraction. User: '{user_prompt}' | Agent: '{agent_response}'")
            print("Structural debug map of Context:", getattr(callback_context, '__dict__', {}))
            return None

        print(f"\n🔍 [Telemetry Catch]\nUser: '{user_prompt}'\nAgent: '{agent_response[:90]}...'")

        # 4. Save clean data straight to your tracking logs
        new_data = pd.DataFrame([{
            "user_prompt": user_prompt,
            "agent_response": agent_response
        }])
        
        if not os.path.exists(LOG_FILE):
            new_data.to_csv(LOG_FILE, index=False)
        else:
            new_data.to_csv(LOG_FILE, mode='a', header=False, index=False)
            
        check_and_run_evaluation()
        
    except Exception as e:
        print(f"\n❌ [CRITICAL LOG ERROR]: {str(e)}")
        
    return None

def check_and_run_evaluation():
    """Triggers an Evidently Report every 5 interactions."""
    if not os.path.exists(LOG_FILE):
        return
    df = pd.read_csv(LOG_FILE)
    print(f"📊 Total entries collected in log: {len(df)}/5")
    
    if len(df) >= 5 and len(df) % 5 == 0:
        print("\n🚀 [Evidently AI] Compiling content quality report...")
        report = Report(metrics=[
            TextEvals(),
            TextLength(column_name="agent_response", alias="Agent Output Length"),
            Sentiment(column_name="agent_response", alias="Agent Response Tone"),
            Contains(column_name="agent_response", items=["error", "fail", "sorry"], mode="any", alias="Failure Rate")
        ])
        report.run(reference_data=None, current_data=df)
        report.save_html("evidently_agent_report.html")
        print("💾 [Evidently AI] Exported to 'evidently_agent_report.html'!")