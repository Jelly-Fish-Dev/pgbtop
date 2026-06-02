from connection import connect
from textual.app import App, ComposeResult
from textual_plot import PlotWidget, HiResMode
import asyncio
import websockets
import json

class PlotApp(App[None]):
    data = []

    def compose(self) -> ComposeResult:
        yield PlotWidget()

    def on_mount(self) -> ComposeResult:
        plot = self.query_one(PlotWidget)
        self.run_worker(self._connect) 
    
    def update(self, data) -> ComposeResult:
        print(data)
        return

    async def _connect(self):
        async with websockets.connect("ws://localhost:8080") as ws:
            async for messages in ws:
                self.DataRecived(messages)
    
    def DataRecived(self, data):
        payload = json.loads(data)
        data_id = payload["data"][0]["id"]
        data_ts = float(payload["data"][0]["value"])
        self.data.append([data_ts, data_id])
        self.updatePlot()

    def updatePlot(self):
        if len(self.data) < 2:
            return
        plot = self.query_one(PlotWidget)
        plot.clear()
        plot.plot(
            x = [row[1] for row in self.data],
            y = [row[0] for row in self.data],
            hires_mode=HiResMode.BRAILLE
        )


if __name__ == "__main__":
    PlotApp().run()
