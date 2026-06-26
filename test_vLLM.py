from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    # vLLM requires a string here but ignores its value locally
    api_key="not-needed-for-local-vllm" 
)

completion = client.chat.completions.create(
    # Match the exact string you passed to 'vllm serve'
    model="Qwen/Qwen2.5-7B-Instruct", 
    messages=[
        {"role": "system", "content": "You are a senior systems engineer."},
        {"role": "user", "content": "What is CAP theoram?."}
    ]
)

print(completion.choices[0].message.content)
