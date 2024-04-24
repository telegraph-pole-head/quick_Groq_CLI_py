import os
import rich_click as click
from groq import Groq
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path
from rich.panel import Panel

# Initialize the Groq client with your API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
console = Console()

click.rich_click.OPTION_GROUPS = {
    "groq_cli.py": [
        {
            "name": "Basic options",
            "options": [
                "--message",
                "--model",
                "--prompt",
            ],
        },
        {
            "name": "Advanced options",
            "options": [
                "--stream-mode",
                "--temperature",
                "--max-tokens",
                "--top-p",
            ],
        },
    ]
}

MODEL_ALIASES = {
    "l3-8": "llama3-8b-8192",
    "l3-70": "llama3-70b-8192",
    "ge": "gemma-7b-it",
    "l2-70": "llama2-70b-4096",
    "mi": "mixtral-8x7b-32768",
}

DEFAULT_MODEL = "l3-70"


def get_models():
    # This function would ideally call Groq's API to list available models
    # For the sake of example, we'll return a static list. Replace with API call if available.
    # return ["llama3-8b-8192","llama3-70b-8192", "gemma-7b-it", "llama2-70b-4096", "mixtral-8x7b-32768"]
    return list(MODEL_ALIASES.keys())


# Function to display model choices and get the actual model identifier
def choose_model():
    console.print("Available models:", style="bold blue")
    for alias, model in MODEL_ALIASES.items():
        console.print(f"[bold magenta]{alias}[/bold magenta] [pink]({model})[/pink]")
    model_alias = click.prompt(
        "Please choose a model alias", default=DEFAULT_MODEL, show_choices=False
    )
    return MODEL_ALIASES.get(model_alias, MODEL_ALIASES[DEFAULT_MODEL])


# Define a dictionary mapping aliases to paths using pathlib
PATH_ALIASES = {
    "def": Path("./prompts/prompt_default.md"),
    "cli": Path("./prompts/cli_helper.md"),
}


def get_prompts():
    return list(PATH_ALIASES.keys())


# Function to read content from the file at the given path
def read_content(file_path):
    try:
        return file_path.read_text()
    except FileNotFoundError:
        console.print(f"[bold red]File not found: {file_path}[/bold red]")
        return ""


@click.command()
@click.option("--message", "-d", prompt="User", help="Your message to the chatbot.")
@click.option(
    "--model",
    "-m",
    type=click.Choice(get_models(), case_sensitive=False),
    default=DEFAULT_MODEL,
    show_default=True,
    help="Choose a model for the chatbot",
)
@click.option(
    "--prompt",
    "-p",
    type=click.Choice(get_prompts(), case_sensitive=False),
    default="def",
    show_default=True,
    help="Alias for file path to read system prompts (optional).",
)
@click.option(
    "--stream-mode",
    "-s",
    type=bool,
    default=False,
    show_default=True,
    help="Stream mode (true or false).",
)
@click.option(
    "--temperature",
    "-t",
    type=float,
    default=1.0,
    help="Temperature for controlling randomness (optional).",
)
@click.option(
    "--max-tokens",
    "-x",
    default=1024,
    show_default=True,
    help="Maximum number of tokens.",
)
@click.option(
    "--top-p",
    "-o",
    type=float,
    default=1.0,
    show_default=True,
    help="Top p for nucleus sampling.",
)
def chat(message, model, prompt, stream_mode, temperature, max_tokens, top_p):
    """Simple CLI chatbot using Groq API with multiple models."""
    try:
        model_name = MODEL_ALIASES[model]
        file_dir = Path(__file__).resolve().parent
        system_prompt = read_content(file_dir / PATH_ALIASES[prompt]) or ""

        # Send user message to Groq API and get response using the selected model
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=stream_mode,
            stop=None,
        )

        # Use Rich to print the chatbot's response
        # console.print(f"[bold magenta]{model_name}:[/bold magenta]")
        # get the chatbot's response
        if stream_mode:
            console.print(f"[bold magenta]{model_name}:[/bold magenta]")
            for chunk in chat_completion:
                response = chunk.choices[0].delta.content or ""
                console.print(response, end="")
        else:
            response = chat_completion.choices[0].message.content or ""
            console.print(
                Panel(
                    Markdown(response),
                    border_style="bold magenta",
                    title=f"Chatbot: {model_name}",
                )
            )

    except Exception as e:
        console.print(Panel(f"{str(e)}", title="[red]Error[/red]", border_style="red"))


if __name__ == "__main__":
    chat()
