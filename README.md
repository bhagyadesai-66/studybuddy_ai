# StudyBuddy AI – Voice-First Learning Assistant

Alexa+ track project for *Build, Ship, Shape: Amazon Developer Hackathon*.
A self-hosted **MCP server (spec 2025-11-25, Streamable HTTP)** that teaches Python, Java, cybersecurity and AI to beginners, plus a mobile web page that works as a **simulated Alexa+ experience** (the rules allow this path).

## Files
| File | Purpose |
|---|---|
| `server.py` | MCP server (endpoint `/mcp`) + study content + web host |
| `index.html` | Mobile chat page (voice in/out, quiz, notes, MCP call log) |
| `test_mcp.py` | Automated tests |

## What you need (all free for the demo)
- Python 3.9+ (nothing to install with pip)
- A GitHub account (you have one)
- Optional: `ANTHROPIC_API_KEY` for live AI answers. **Not needed** – demo mode works without it.
- Optional: a free host (Render / Codespaces) for a public HTTPS link.

## Run
```
python server.py
```
Open http://127.0.0.1:8800 . Test: `python test_mcp.py`

## Tools exposed over MCP
`list_topics`, `explain_concept`, `revision_notes`, `quiz_question`, `check_answer`

## Privacy
Questions are never stored or logged. The API key lives only on the server (environment variable).

## Alexa+ status
- Done and tested: MCP server, tool calls, web simulation, demo mode.
- NOT tested on a real Alexa+ device. Real connection needs Alexa+ developer preview access and a public HTTPS URL for `/mcp`. See the hackathon Resources page.

## What was built during the hackathon
The project was upgraded from an earlier AI Study Assistant: MCP server, voice-first interface, quiz, notes, demo mode.
