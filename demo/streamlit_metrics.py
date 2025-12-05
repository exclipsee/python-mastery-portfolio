from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Live Metrics", layout="wide")
st.title("Live System Metrics (WebSocket)")
st.write(
  "This demo opens a WebSocket from your browser to the API `/ws/metrics`"
  " endpoint and renders live charts."
)

ws_default = st.text_input("WebSocket URL", value="ws://localhost:8000/ws/metrics")
st.markdown("---")

html = f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
      body {{
        font-family: Arial, Helvetica, sans-serif;
        margin: 0;
        padding: 0;
      }}
      .grid {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 12px;
        padding: 12px;
      }}
      .card {{
        background: #fff;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
      }}
    </style>
  </head>
  <body>
    <div class="grid">
      <div class="card"><canvas id="cpu"></canvas></div>
      <div class="card"><canvas id="memory"></canvas></div>
      <div class="card"><canvas id="disk"></canvas></div>
    </div>
    <script>
      const wsUrl = '{ws_default}';

      function makeChart(ctx, label, color) {{
        return new Chart(ctx, {{
          type: 'line',
          data: {{
            labels: [],
            datasets: [{{ label: label, data: [], borderColor: color, tension: 0.2 }}]
          }},
          options: {{
            animation: false,
            scales: {{ x: {{ display: true }}, y: {{ beginAtZero: true }} }}
          }}
        }});
      }}

      const cpuChart = makeChart(
        document.getElementById('cpu').getContext('2d'),
        'CPU %',
        'rgba(255,99,132,1)'
      );
      const memChart = makeChart(
        document.getElementById('memory').getContext('2d'),
        'Memory %',
        'rgba(54,162,235,1)'
      );
      const diskChart = makeChart(
        document.getElementById('disk').getContext('2d'),
        'Disk %',
        'rgba(75,192,192,1)'
      );

      function pushSample(chart, label, value) {{
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);
        if (chart.data.labels.length > 30) {{
          chart.data.labels.shift();
          chart.data.datasets[0].data.shift();
        }}
        chart.update('none');
      }}

      function connect() {{
        let socket;
        try {{
          socket = new WebSocket(wsUrl);
        }} catch (e) {{
          console.error('WebSocket construction failed', e);
          return;
        }}
        socket.onopen = () => console.info('WebSocket open');
        socket.onclose = () => console.info('WebSocket closed');
        socket.onerror = (e) => console.error('WebSocket error', e);
        socket.onmessage = (evt) => {{
          try {{
            const msg = JSON.parse(evt.data);
            if (msg.type === 'system_metrics' && msg.data) {{
              const d = msg.data;
              const ts = new Date(d.timestamp * 1000).toLocaleTimeString();
              pushSample(cpuChart, ts, Math.round(d.cpu_percent * 100)/100);
              pushSample(memChart, ts, Math.round(d.memory_percent * 100)/100);
              pushSample(diskChart, ts, Math.round(d.disk_usage_percent * 100)/100);
            }}
          }} catch (e) {{
            console.error('Failed to parse message', e);
          }}
        }};
      }}

      connect();
    </script>
  </body>
</html>
"""

st.components.v1.html(html, height=520)
