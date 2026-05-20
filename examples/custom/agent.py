import argparse
from json import tool
import os
import sys

from deepagents import create_deep_agent
from langchain.tools import tool
from deepagents.backends import FilesystemBackend, LocalShellBackend
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from rich.console import Console
from rich.panel import Panel
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

console = Console()



def create_custom_deep_agent():

    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Initialize Claude Sonnet 4.5 for toolkit initialization

    #model = ChatAnthropic(model="Qwen3.6-27B-MTP:Q3_K_M", temperature=0.6)
    #model = ChatAnthropic(model="Qwen3.6-27B-MTP:Q3_K_M", temperature=1)

    model = ChatAnthropic(model="Qwen3.6-27B-MTP:Q4_K_M", temperature=0.6)
    #model = ChatAnthropic(model="Qwen3.6-27B-MTP:Q4_K_M", temperature=1)



    #model = ChatAnthropic(model="Qwen3.6-35B-A3B-MTP:Q3_K_M ", temperature=0.6)
    #model = ChatAnthropic(model="Qwen3.6-35B-A3B-MTP:Q4_K_M ", temperature=0.6)

    # Create the Deep Agent with all parameters
    agent = create_deep_agent(
        model=model,  # Claude Sonnet 4.5 with temperature=0
        memory=["./AGENTS.md"],  # Agent identity and general instructions
        skills=[
            "./skills/"
        ],
       # tools=[],  # SQL database tools
        subagents=[],  # No subagents needed
        backend=LocalShellBackend(root_dir=base_dir)
        #backend=FilesystemBackend(root_dir=base_dir),  # Persistent file storage
    )

    return agent

def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.standaard.be")
        #яhref = page.evaluate('() => document.location.href')
        print(page.content())
        browser.close()

def main():
    parser = argparse.ArgumentParser(
        description="Text-to-SQL Deep Agent powered by LangChain Deep Agents and Claude Sonnet 4.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py "What are the top 5 best-selling artists?"
  python agent.py "Which employee generated the most revenue by country?"
  python agent.py "How many customers are from Canada?"
        """,
    )
    parser.add_argument(
        "question",
        type=str,
        help="Natural language question to answer using the Chinook database",
    )

    args = parser.parse_args()

    # Display the question
    console.print(
        Panel(f"[bold cyan]Question:[/bold cyan] {args.question}", border_style="cyan")
    )
    console.print()

    # Create the agent
    console.print("[dim]Creating SQL Deep Agent...[/dim]")
    agent = create_custom_deep_agent()

    # Invoke the agent
    console.print("[dim]Processing query...[/dim]\n")

    try:

        #browser()

        result = agent.invoke(
            {"messages": [{"role": "user", "content": args.question}]}
        )

        # Extract and display the final answer
        final_message = result["messages"][-1]
        answer = (
            final_message.content
            if hasattr(final_message, "content")
            else str(final_message)
        )

        console.print(
            Panel(f"[bold green]Answer:[/bold green]\n\n{answer}", border_style="green")
        )

    except Exception as e:
        console.print(
            Panel(f"[bold red]Error:[/bold red]\n\n{str(e)}", border_style="red")
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
