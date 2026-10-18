# Devpost copy-paste text

**Project name:** StudyBuddy AI – Voice-First Learning Assistant

**Tagline:** A voice-first study buddy that explains Python, Java, cybersecurity and AI in simple steps, built as an MCP server for Alexa+.

**Track:** Alexa+ (primary). Optional mini challenge: Open Source (MIT license included).

## About the project
**Inspiration.** As a beginner engineering student, I found programming and security terms hard to understand. I wanted a study buddy I can simply ask out loud and get a short, clear answer.

**What it does.** StudyBuddy AI answers beginner questions about Python, Java, cybersecurity and AI with a one-line answer followed by simple steps. It also gives revision notes and a beginner quiz with instant feedback. Answers are short so they sound natural when spoken.

**How I built it.** The core is a self-hosted MCP server (spec 2025-11-25, Streamable HTTP) written in Python with no extra libraries. It exposes five tools: list_topics, explain_concept, revision_notes, quiz_question and check_answer. An Alexa+ agent can call these tools. Because I do not have a real Alexa+ device, I also built a mobile web page that acts as a simulated Alexa+ experience: it uses the microphone and speech output of the browser and talks to the server only through real MCP calls, with a visible call log.

**Privacy and safety.** Student questions are never stored or logged. The optional AI key stays on the server only. Without a key, demo mode answers from built-in lessons, so the app never breaks.

**Challenges.** Keeping answers short enough for voice, and making the server work without any paid service.

**What I learned.** How MCP works (initialize, tools/list, tools/call) and how to design for voice.

**What's next.** More subjects, Kannada explanations, and testing on a real Alexa+ device.

**Built with:** Python, MCP (Streamable HTTP), HTML, CSS, JavaScript, Web Speech API, Render (hosting), GitHub

**What I built during the hackathon (existing project):** I started from my earlier AI Study Assistant website. During the submission window I built the MCP server, the voice-first interface, the quiz and notes tools, demo mode and the automated tests.

## Product feedback (fill in with YOUR real experience before submitting)
For each tool you used (MCP spec, Alexa+ resources, Render, etc.), write 3 to 5 plain sentences:
- What I used it for:
- What worked well:
- What needs work:
- How onboarding felt:
- Would I build with it again:
