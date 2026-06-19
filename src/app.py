import json
import httpx
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Select, TextArea, Button, Static, TabbedContent, TabPane

class ApiClientApp(App):
    """A sleek, lightning-fast Terminal API Client."""

    CSS = """
    Screen {
        background: #1a1a1a;
    }
    #url_bar {
        height: 3;
        margin: 1;
        layout: horizontal;
    }
    #method_select {
        width: 15%;
        margin-right: 1;
    }
    #url_input {
        width: 70%;
        margin-right: 1;
    }
    #send_btn {
        width: 15%;
    }
    #workspace {
        height: 1fr;
        margin: 0 1 1 1;
    }
    .pane {
        width: 50fr;
        border: solid #333333;
        padding: 1;
    }
    #response_meta {
        background: #262626;
        padding: 0 1;
        margin-bottom: 1;
        color: #00ff00;
        height: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+s", "send_request", "Send Request")
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Top Address & Configuration Bar
        with Horizontal(id="url_bar"):
            yield Select(
                options=[("GET", "GET"), ("POST", "POST"), ("PUT", "PUT"), ("DELETE", "DELETE")],
                value="GET",
                id="method_select"
            )
            yield Input(placeholder="Enter request URL (e.g., https://httpbin.org)", id="url_input")
            yield Button("Send 🚀", variant="success", id="send_btn")

        # Main Split Workspace
        with Horizontal(id="workspace"):
            # Left Panel: Request Configuration Builder
            with Vertical(classes="pane"):
                with TabbedContent():
                    with TabPane("Headers"):
                        yield TextArea('{\n  "User-Agent": "TerminalClient/1.0"\n}', language="json", id="req_headers")
                    with TabPane("JSON Body"):
                        yield TextArea('{\n  "key": "value"\n}', language="json", id="req_body")

            # Right Panel: Dynamic Live Response Box
            with Vertical(classes="pane"):
                yield Static("Status: --- | Time: ---", id="response_meta")
                yield TextArea(read_only=True, language="json", id="response_body")

        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_btn":
            await self.action_send_request()

    async def action_send_request(self) -> None:
        """Executes the network request via HTTPX and updates the TUI interface state."""
        url = self.query_one("#url_input", Input).value
        method = self.query_one("#method_select", Select).value
        res_body_widget = self.query_one("#response_body", TextArea)
        res_meta_widget = self.query_one("#response_meta", Static)

        if not url:
            res_body_widget.text = "Error: URL field cannot be left blank."
            return

        # Append default scheme if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        res_body_widget.text = "Sending request..."

        # Parse configuration data
        try:
            headers = json.loads(self.query_one("#req_headers", TextArea).text)
        except Exception:
            headers = {}

        data = None
        if method in ["POST", "PUT"]:
            try:
                data = json.loads(self.query_one("#req_body", TextArea).text)
            except Exception:
                data = None

        # Execute Request asynchronously
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=headers, json=data, timeout=10.0)

                # Format Metadata Status Header
                res_meta_widget.update(f"Status: [bold]{response.status_code}[/] | Time: {response.elapsed.total_seconds():.3f}s")

                # Handle and format JSON output safely
                try:
                    res_body_widget.text = json.dumps(response.json(), indent=2)
                except Exception:
                    res_body_widget.text = response.text

            except Exception as e:
                res_meta_widget.update("Status: ERROR")
                res_body_widget.text = f"An execution error occurred:\n{str(e)}"

def main():
    app = ApiClientApp()
    app.run()

if __name__ == "__main__":
    main()
