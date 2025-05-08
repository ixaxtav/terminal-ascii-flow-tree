import json
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from collections import defaultdict
from pathlib import Path

def load_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data.get("nodes", []), data.get("links", [])

def colored_flow_symbol(value, scale=50):
    length = min(max(1, value // scale), 10)
    return Text("=" * length + ">", style="green")

def build_index_name_map(nodes):
    return {i: node["name"] for i, node in enumerate(nodes)}

def build_inflows(links):
    inflows = defaultdict(list)
    for link in links:
        inflows[link["target"]].append(link)
    return inflows

def render_data(console, nodes, links):
    index_to_name = build_index_name_map(nodes)
    children = defaultdict(list)
    for link in links:
        children[link["source"]].append(link)

    inflows = build_inflows(links)
    root_nodes = set(children.keys()) - set(inflows.keys())

    def print_node(node_idx, prefix=""):
        node_name = index_to_name[node_idx]
        console.print(f"{prefix}[bold]{node_name}[/bold]")
        if node_idx in children:
            for idx, link in enumerate(children[node_idx]):
                branch = "└──" if idx == len(children[node_idx]) - 1 else "├──"
                flow = colored_flow_symbol(link["value"])
                target_name = index_to_name[link["target"]]
                label = Text(f"{prefix}{branch} ") + flow + Text(f" {target_name} ({link['value']})")
                console.print(label)
                print_node(link["target"], prefix + ("    " if idx == len(children[node_idx]) - 1 else "│   "))

    for node_idx in sorted(root_nodes):
        print_node(node_idx)

def main():
    console = Console()
    filepath = Prompt.ask("Enter the path to your JSON file", default="sample.json")

    if not Path(filepath).exists():
        console.print(f"[red]File not found:[/red] {filepath}")
        return

    nodes, links = load_data(filepath)
    render_data(console, nodes, links)

if __name__ == "__main__":
    main()
