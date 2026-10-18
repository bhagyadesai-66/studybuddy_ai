"""StudyBuddy AI - Voice-First Learning Assistant.
One file: MCP server (Streamable HTTP, spec 2025-11-25) + web app host.
Python 3.9+, nothing to install.  Run:  python server.py
Optional: set ANTHROPIC_API_KEY on the SERVER for AI answers. No key = demo mode.
Privacy: questions are never saved or logged."""
import json, os, random, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PROTOCOL = "2025-11-25"
API_KEY = os.environ.get("ANTHROPIC_API_KEY")  # server-side only, never sent to browser
MODEL = os.environ.get("STUDYBUDDY_MODEL", "claude-haiku-5-5")
HERE = Path(__file__).parent

# ---- Study content (edit this to add topics) -------------------------------
# concept: (one-line answer, [steps])
TOPICS = {
 "python": {
  "concepts": {
   "variable": ("A variable is a labeled box that stores a value.", ["Pick a name, like age.", "Store a value: age = 18.", "Use it later: print(age)."]),
   "loop": ("A loop repeats code so you do not write it many times.", ["Write: for i in range(3):", "Indent the lines to repeat.", "Python runs them 3 times."]),
   "function": ("A function is a reusable block of code with a name.", ["Start with: def greet():", "Indent the code inside.", "Run it by writing greet()."])},
  "notes": ["Python uses indentation instead of braces.", "Use print() to show output.", "Lists use [ ], dictionaries use { }."],
  "quiz": [("Which symbol stores a value in a variable?", ["=", "==", "->"], 0), ("Which keyword makes a function?", ["func", "def", "fun"], 1)]},
 "java": {
  "concepts": {
   "class": ("A class is a blueprint for making objects.", ["Write: class Student { }", "Add fields like name.", "Make one: new Student()."]),
   "method": ("A method is a named action inside a class.", ["Write: void sayHi() { }", "Put code inside the braces.", "Call it: obj.sayHi();"]),
   "array": ("An array stores many values of the same type.", ["Declare: int[] marks = new int[3];", "Set: marks[0] = 90;", "Counting starts at 0."])},
  "notes": ["Every Java program starts at main().", "Java is strongly typed: declare int, String, etc.", "File name must match the public class name."],
  "quiz": [("Where does a Java program start?", ["start()", "main()", "run()"], 1), ("First index of an array is?", ["0", "1", "-1"], 0)]},
 "cybersecurity": {
  "concepts": {
   "phishing": ("Phishing is a fake message that tricks you into giving away secrets.", ["Check the sender address.", "Do not click unexpected links.", "Report and delete it."]),
   "password": ("A strong password is long, unique, and hard to guess.", ["Use 12 or more characters.", "Never reuse passwords.", "Turn on two-factor login."]),
   "encryption": ("Encryption scrambles data so only the key holder can read it.", ["Readable data goes in.", "A key scrambles it.", "Only the right key unscrambles it."])},
  "notes": ["Update your software often.", "Two-factor login blocks most account theft.", "Public Wi-Fi is risky for private data."],
  "quiz": [("Best defense against stolen passwords?", ["Two-factor login", "Shorter password", "Same password everywhere"], 0), ("A fake email asking for your bank PIN is?", ["Encryption", "Phishing", "Backup"], 1)]},
 "ai": {
  "concepts": {
   "machine learning": ("Machine learning lets computers learn patterns from examples.", ["Collect examples.", "Train a model to find patterns.", "Use it to predict new cases."]),
   "neural network": ("A neural network is layers of simple math units that learn together.", ["Input goes into the first layer.", "Each layer passes numbers on.", "Training adjusts the connections."]),
   "training data": ("Training data is the set of examples a model learns from.", ["Gather many examples.", "Label them if needed.", "Better data gives a better model."])},
  "notes": ["AI learns from data, not hand-written rules.", "A model is only as good as its training data.", "Always check AI answers for mistakes."],
  "quiz": [("What does a model learn from?", ["Training data", "The monitor", "Wi-Fi"], 0), ("ML stands for?", ["Machine Learning", "Max Level", "Main Loop"], 0)]},
}

def ask_ai(topic, question):
    """Optional live AI. Returns None on any problem so demo mode takes over."""
    if not API_KEY:
        return None
    try:
        body = {"model": MODEL, "max_tokens": 300,
                "system": "You are StudyBuddy, a patient tutor for beginners. Answer in simple English: one short sentence, then at most 3 numbered steps.",
                "messages": [{"role": "user", "content": f"Topic: {topic}. Question: {question}"}]}
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
              {"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)["content"][0]["text"]
    except Exception:
        return None

# ---- Tools ------------------------------------------------------------------
def t_list_topics(a):
    qs = {t: [f"What is {'an' if c[0] in 'aeiou' else 'a'} {c}?" for c in d["concepts"]] for t, d in TOPICS.items()}
    return {"text": "Topics: " + ", ".join(TOPICS) + ". Ask me about any of them.", "data": {"topics": qs}}

def t_explain(a):
    topic, q = a.get("topic", "").lower(), a.get("question", "").lower()
    if topic not in TOPICS:
        return {"text": "I can help with python, java, cybersecurity, or ai. Which one?"}
    live = ask_ai(topic, q)
    if live:
        return {"text": live, "data": {"mode": "ai"}}
    for name, (short, steps) in TOPICS[topic]["concepts"].items():
        if name in q:
            return {"text": short + " " + " ".join(f"Step {i}: {s}" for i, s in enumerate(steps, 1)), "data": {"mode": "demo"}}
    return {"text": f"Demo mode: I know {', '.join(TOPICS[topic]['concepts'])} in {topic}. Try asking about one of them.", "data": {"mode": "demo"}}

def t_notes(a):
    t = a.get("topic", "").lower()
    if t not in TOPICS:
        return {"text": "Choose python, java, cybersecurity, or ai."}
    return {"text": f"Quick notes on {t}: " + " ".join(f"{i}. {n}" for i, n in enumerate(TOPICS[t]["notes"], 1))}

def t_quiz(a):
    t = a.get("topic", "").lower()
    if t not in TOPICS:
        return {"text": "Choose python, java, cybersecurity, or ai."}
    i = random.randrange(len(TOPICS[t]["quiz"]))
    q, opts, _ = TOPICS[t]["quiz"][i]
    return {"text": q + " " + " ".join(f"Option {n}: {o}." for n, o in enumerate(opts, 1)), "data": {"id": i, "question": q, "options": opts}}

def t_check(a):
    try:
        q, opts, ans = TOPICS[a["topic"].lower()]["quiz"][int(a["question_id"])]
        ok = int(a["choice"]) == ans
    except (KeyError, ValueError, IndexError):
        return {"text": "I could not check that answer."}
    return {"text": ("Correct! " if ok else f"Not quite. The answer is {opts[ans]}. ") + "Want another question?", "data": {"correct": ok}}

def schema(**props):
    return {"type": "object", "properties": {k: {"type": v} for k, v in props.items()}, "required": list(props)}

TOOLS = {
 "list_topics": (t_list_topics, "List study topics and sample questions.", {"type": "object", "properties": {}}),
 "explain_concept": (t_explain, "Explain a Python, Java, cybersecurity or AI concept in simple steps.", schema(topic="string", question="string")),
 "revision_notes": (t_notes, "Give 3 short revision notes for a topic.", schema(topic="string")),
 "quiz_question": (t_quiz, "Ask one beginner multiple-choice question.", schema(topic="string")),
 "check_answer": (t_check, "Check a quiz answer (choice is the 0-based option number).", schema(topic="string", question_id="integer", choice="integer")),
}

# ---- MCP over Streamable HTTP ------------------------------------------------
def handle(msg):
    m, i = msg.get("method"), msg.get("id")
    ok = lambda r: {"jsonrpc": "2.0", "id": i, "result": r}
    err = lambda c, s: {"jsonrpc": "2.0", "id": i, "error": {"code": c, "message": s}}
    if i is None:
        return None  # notifications get no reply
    if m == "initialize":
        return ok({"protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
                   "serverInfo": {"name": "studybuddy-ai", "version": "1.0.0"}})
    if m == "ping":
        return ok({})
    if m == "tools/list":
        return ok({"tools": [{"name": n, "description": d, "inputSchema": s} for n, (_, d, s) in TOOLS.items()]})
    if m == "tools/call":
        p = msg.get("params", {})
        if p.get("name") not in TOOLS:
            return err(-32602, "Unknown tool")
        r = TOOLS[p["name"]][0](p.get("arguments") or {})
        out = {"content": [{"type": "text", "text": r["text"]}]}
        if "data" in r:
            out["structuredContent"] = r["data"]
        return ok(out)
    return err(-32601, "Method not found")

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # privacy: no request logging

    def reply(self, code, body=b"", ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/":
            self.reply(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif p == "/health":
            self.reply(200, json.dumps({"ok": True, "mode": "ai" if API_KEY else "demo"}).encode())
        else:
            self.reply(405 if p == "/mcp" else 404)

    def do_POST(self):
        if urlparse(self.path).path != "/mcp":
            return self.reply(404)
        origin = self.headers.get("Origin")  # block other websites (DNS-rebinding protection)
        if origin and urlparse(origin).netloc != self.headers.get("Host"):
            return self.reply(403)
        try:
            msg = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            res = handle(msg)
        except Exception:
            return self.reply(400, b'{"jsonrpc":"2.0","id":null,"error":{"code":-32700,"message":"Bad request"}}')
        self.reply(202) if res is None else self.reply(200, json.dumps(res).encode())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8800))
    host = os.environ.get("HOST", "0.0.0.0" if "PORT" in os.environ else "127.0.0.1")  # hosting sites set PORT
    print(f"StudyBuddy AI on http://{host}:{port}  (MCP: /mcp)  mode: {'AI' if API_KEY else 'demo'}")
    ThreadingHTTPServer((host, port), H).serve_forever()
