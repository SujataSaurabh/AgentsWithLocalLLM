 from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    # vLLM requires a string here but ignores its value locally
    api_key="not-needed-for-local-vllm" 
)

completion = client.chat.completions.create(
    # CHANGE THIS: Match the exact string you passed to 'vllm serve'
    model="Qwen/Qwen2.5-7B-Instruct", 
    messages=[
        {"role": "system", "content": "You are a senior systems engineer."},
        {"role": "user", "content": "Give me a high-level strategy for multi-tenant data isolation in an LLM pipeline."}
    ]
)

print(completion.choices[0].message.content)
