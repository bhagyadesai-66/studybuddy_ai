"""Run:  python test_mcp.py   (starts its own server on port 8899, no key needed)"""
import json, threading, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
import server

httpd = ThreadingHTTPServer(("127.0.0.1", 8899), server.H)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:8899"

def post(body, origin=None):
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if origin:
        h["Origin"] = origin
    req = urllib.request.Request(URL + "/mcp", json.dumps(body).encode(), h)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        return e.code, None

def call(name, args):
    return post({"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": name, "arguments": args}})[1]["result"]

s, r = post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}})
assert s == 200 and r["result"]["protocolVersion"] == "2025-11-25"; print("PASS initialize")
assert post({"jsonrpc": "2.0", "method": "notifications/initialized"})[0] == 202; print("PASS notification returns 202")
tools = post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})[1]["result"]["tools"]
assert len(tools) == 5; print("PASS tools/list:", [t["name"] for t in tools])
txt = call("explain_concept", {"topic": "python", "question": "What is a loop?"})["content"][0]["text"]
assert "repeats" in txt and "Step 1" in txt; print("PASS explain (demo mode):", txt[:60], "...")
assert "ai" in call("list_topics", {})["structuredContent"]["topics"]; print("PASS list_topics")
q = call("quiz_question", {"topic": "java"})["structuredContent"]
assert "Correct" in call("check_answer", {"topic": "java", "question_id": 1, "choice": 0})["content"][0]["text"]; print("PASS quiz + check_answer")
assert "Choose" in call("revision_notes", {"topic": "x"})["content"][0]["text"]; print("PASS unknown topic handled")
assert post({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "nope"}})[1]["error"]["code"] == -32602; print("PASS unknown tool error")
assert post({"jsonrpc": "2.0", "id": 4, "method": "ping"}, origin="http://evil.example")[0] == 403; print("PASS foreign Origin blocked")
assert urllib.request.urlopen(URL + "/").status == 200; print("PASS web page served")
assert json.load(urllib.request.urlopen(URL + "/health"))["mode"] == "demo"; print("PASS health = demo mode")
print("\nALL TESTS PASSED")
