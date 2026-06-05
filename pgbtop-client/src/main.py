"""Demo of Textual"""
import json
import websockets

from textual.app import App, ComposeResult
from textual_plot import PlotWidget, HiResMode


class PlotApp(App[None]):
    """Demo of Textual"""

    data = []

    def compose(self) -> ComposeResult:
        """Build the UI — yields a single PlotWidget that fills the terminal."""
        yield PlotWidget()

    def on_mount(self) -> ComposeResult:
        """On startup, find the plot widget and start the WebSocket connection worker."""
        self.run_worker(self._connect)

    def update(self, data) -> ComposeResult:
        """Handle incoming data — placeholder, currently prints to stdout."""
        print(data)

    async def _connect(self):
        """Open a WebSocket connection to the pgbtop server and listen for messages."""
        async with websockets.connect("ws://localhost:8080") as ws:
            async for messages in ws:
                self.data_recived(messages)

    def data_recived(self, data):
        """Parse an incoming JSON message and append the data point to the local buffer."""
        payload = json.loads(data)
        data_id = payload["data"][0]["id"]
        data_ts = float(payload["data"][0]["value"])
        self.data.append([data_ts, data_id])
        self.update_plot()

    def update_plot(self):
        """Re-render the plot widget with the current data buffer."""
        if len(self.data) < 2:
            return
        plot = self.query_one(PlotWidget)
        plot.clear()
        plot.plot(
            x=[row[1] for row in self.data],
            y=[row[0] for row in self.data],
            hires_mode=HiResMode.BRAILLE,
        )


if __name__ == "__main__":
    PlotApp().run()
