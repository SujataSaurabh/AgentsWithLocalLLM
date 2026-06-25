# Set up vLLM and a weather agent with Google's adk 

## Set up vLLM on M4 Max GPU
1. Set up steps for vLLM installationa on MAC M4 Max GPU

```> python3 -c "import platform; print(platform.machine())"```

```arm-64```

2. download and execute the Official metal installer
   
```> curl -fsSL https://raw.githubusercontent.com/vllm-project/vllm-metal/main/install.sh | bash```

4. Activate the environment

```> source ~/.venv-vllm-metal/bin/activate```

4. Confirm MLX sees your M4 Max GPU

```> python -c "import mlx.core as mx; print(f'MLX default hardware device: {mx.default_device()}')"```

```Output should be: MLX default hardware device: Device(gpu, 0)```

5. Check where is the model saved with its size
   
```> du -sh ~/.cache/huggingface/hub/*```

7. Run the model
   
```> vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000```

Here ```--enable-auto-tool-choice ``` tells your local vLLM instance that it is allowed to accept incoming requests using OpenAI's structured "tool_choice": "auto" format.

```--tool-call-parser hermes``` tells vLLM to use the Hermes parser template, which is the exact tool layout Qwen 2.5 was natively trained on to output function parameters safely without formatting bugs.

```> vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000 --enable-auto-tool-choice --tool-call-parser hermes ```

7. Run your test script

```> python vLLM_test.py```

## weather agent with Google's adk 
1. Install the core Google ADK framework

```> pip install google-adk```

2. Scaffold a clean agent project
   
```> adk create weather_agent```

```> cd weather_agent```

This creates a standardized project structure including a critical configuration setup and an ```agent.py``` template file. Write the weather app code in ```agent.py```. Register your agent 
```__init.py__``` file. 

3. Run your agent (Chat in the terminal)

```> adk run weather_agent```

4. Run your agent (Web UI Cockpit)

```> adk web --port 8080```

Open  browser and navigate to ```http://localhost:8080```. This loads the visual testing playground where you can select your agent, track execution logic, and view real-time token performance metadata.



