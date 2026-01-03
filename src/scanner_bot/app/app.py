from __future__ import annotations

import os
import dash
from dash import html


app = dash.Dash(__name__)
app.title = "Scanner"

app.layout = html.Div(
    "Hello World",
    style={"fontFamily": "system-ui", "padding": "24px", "fontSize": "24px"},
)


def main() -> None:
    app.run(
        debug=True,
        host=os.getenv("DASH_HOST", "127.0.0.1"),
        port=int(os.getenv("DASH_PORT", "8050")),
    )


if __name__ == "__main__":
    main()
