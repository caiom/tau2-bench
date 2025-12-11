# Overview of changes

The way that tau2-bench works is that it uses LiteLLM as a wrapper around different model provider APIs. When evaluating local models, we use vLLM API server to run the model with an OpenAI-compatible API.

However, our model checkpoints are unreliable at generating properly formatted tool calls. If the model produces an invalid tool call, vLLM will return an error over the API, which causes LiteLLM to throw an exception on the client side. Similarly, exceeding the model's context limit will also lead to an exception in client side code.

It appears that the tau2-bench code assumes a perfectly reliable API. Any exception in LiteLLM causes the entire benchmark to crash. We would instead prefer that an API error should only cause the single corresponding test case to be marked as failing, instead of halting the entire benchmarking run. (This is a [known issue on Github](https://github.com/sierra-research/tau2-bench/issues/42) but it has not been fixed.)

As a workaround, I have added new exception handling to the tau2-bench code.
- In `data_model/simulation.py` new error types are added to the `TerminationReason` enum.
- In `orchestrator/orchestrator.py` there is now a try-except block around `self.step()`

# Installing

See the `README` for more info.

```bash
cd tau2-bench
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

# Running

To run with local model checkpoints, first launch vLLM inference server.

```bash
vllm serve /path/to/model/directory \
    --port 8000 \
    --served-model-name phi-tool \
    --tool-call-parser phi4_mini_json \
    --enable-auto-tool-choice \
```

The Telecom domain has a "solo agent" model that does not depend on a user simulator LLM. This can be run with the following:

```bash
tau2 run \
    --domain telecom \
    --agent llm_agent_solo \
    --agent-llm hosted_vllm/phi-tool \
    --agent-llm-args '{"api_base": "http://localhost:8000/v1"}' \
    --user dummy_user \
```

For more sophisticated benchmarking scenarios, the user is simulated by an OpenAI model. See documentation here for using Azure OpenAI with LiteLLM and obtaining authentication tokens: https://docs.litellm.ai/docs/providers/azure/

```bash
tau2 run \
    --domain telecom \
    --agent-llm hosted_vllm/phi-tool \
    --agent-llm-args '{"api_base": "http://localhost:8000/v1"}' \
    --user_llm azure/gpt-4.1 \
    --agent-llm-args '{"api_base": "your_azure_openai_endpoint", "azure_ad_token": "..."}' \
```
