# Local LLM Modular Resource

`local-llm` is a modular resource that provides local LLM inference capabilities for machines running on the Viam platform.

The default model at this time is [TinyLlama 1.1B](https://huggingface.co/second-state/TinyLlama-1.1B-Chat-v1.0-GGUF).
Other models can be used, as long as they are compatible with llama.cpp (see [Config options llm_repo and llm_file](#config)).
Also please keep in mind that some models will not run well on specific hardware.

## Prerequisites

The machine using this module must have Python 3.8+ and pip installed on the system.
python venv must also be installed:

``` bash
apt install python3.11-venv
```

Where the python version may need to be modified based on the python version on your machine.

## Config

**llm_repo** (Optional): The HuggingFace repo id used to download the model.  Defaults to "second-state/TinyLlama-1.1B-Chat-v1.0-GGUF"

**llm_file** (Optional): The HuggingFace file used to download the model.  Must be specified if *llm_repo* is specified. Defaults to "tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf"

**system_message** (Optional): The context for the chat system to use when interpreting input from the user. Defaults to "A chat between a curious user and an artificial intelligence assistant. The assistant must start by introducing themselves as 'The Great Provider'. The assistant gives helpful, detailed, and polite answers to the user's questions."

**n_gpu_layers** (Optional): Number of layers to offload to GPU (-ngl). If -1, all layers are offloaded. Defaults to 0.

**temperature** (Optional): Float value to determine the randomness of the responses from the model. A high temperature, i.e. 5, would result in very different values while running the same prompt repeatedly. A value that's too low, i.e. 0.2, would result in more "robotic" responses. Default value is 0.75.

The following is an example configuration for this resource's attributes based on the default values:

```json
{
    "system_message": "A chat between a curious user and an artificial intelligence assistant. The assistant must start by introducing themselves as 'The Great Provider'. The assistant gives helpful, detailed, and polite answers to the user's questions.",
    "n_gpu_layers": 0,
    "temperature": 0.75
}
```

This is an example of using default settings with a [different model](https://huggingface.co/Qwen/Qwen1.5-0.5B-Chat-GGUF/blob/main/qwen1_5-0_5b-chat-q5_k_m.gguf):

```json
{
    "llm_repo": "Qwen/Qwen1.5-0.5B-Chat-GGUF",
    "llm_file": "qwen1_5-0_5b-chat-q5_k_m.gguf"
}
```

## Usage

This module is built as a [Chat service](https://github.com/viam-labs/chat-service-api) that has a single method called "chat".

```python
from chat_service_api import Chat

// machine connection logic above

llm = Chat.from_robot(robot, name="llm")
response = await llm.chat("What is the meaning of life?")
print(response)
```

```go
import chat "github.com/viam-labs/chat-service-api/src/chat_go"

llm, err := chat.FromRobot(robot, "llm")
resp, err := llm.Chat(ctx, "What is the meaning of life?")
fmt.Println(resp)
```

See the [`examples/client.py`](./examples/client.py) for a complete demo program.

## Contributing 

This project is bootstrapped with [Pyprojectx](https://github.com/pyprojectx/pyprojectx) and manages dependencies with [PDM](https://pdm-project.org/latest/#introduction) for modern Python development. The various commands for managing the project are collected under the `Makefile`.

### Setup development environment

If Python is not available, install it using a tool version manager like [`mise`](https://mise.jdx.dev/), which will automatically use the `.tool-versions` config in this project.

Then run:

```console
make install
```

### Build the project

```console
make build
```

### Publish module to Viam

Bump the package version:

```console
./pw pdm bump auto
```

Build and publish new version:

```console
version=$(./pw pdm show --version) make publish
```
