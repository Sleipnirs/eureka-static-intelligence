# Example — compiling the dental-clinic chatbox

```bash
python main.py examples/input_dental.json
```

Expected result JSON: `status: ok`, ~26 nodes, Quick-10 from mainline flags,
`out/sunny-dental-clinic-chatbox.html` around 47 KB.

Open the HTML in any browser (or `python -m http.server` and visit it):
- ask "how much for a cleaning" / "洗牙贵不贵" → price answer
- type "thanks!" / "谢谢医生" → warm acknowledgment, never a wrong answer
- type "23*45+12" → instant calculation + calculator card
- ask something off-map ("tokyo weather?") → did-you-mean / Google-AI card
- click ↻ to reset · ☾ dark mode · 文 language toggle
