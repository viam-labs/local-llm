# Local LLM Modular Resource

`local-llm` is a modular resource that provides local LLM inference capabilities for machines running on the Viam platform.

## Prerequisites

The machine using this module must have Python 3.8+ installed on the system.

## Config

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

## Usage

This module is built as a [Generic component](https://docs.viam.com/components/generic/#api) that follows a single command called "chat" through the [`DoCommand` / `do_command` method](https://docs.viam.com/components/generic/#docommand)

```python
// machine connection logic above

llm = Generic.from_robot(robot, name="llm")
response = await llm.do_command({"chat": ["What is the meaning of life?"]})
print(response["chat"])
```

```go
llm, err := generic.FromRobot(robot, "llm")
resp, err := llm.DoCommand(ctx, map[string]interface{}{"chat": ["What is the meaning of life?"]})
fmt.Println(resp["chat"])
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

### Build the project:

```console
make build
```

### Publish module to Viam

```console
make publish
```
