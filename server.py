import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.agents.orchestrator import TruthGuardOrchestrator

CORPUS_PATH = os.path.join(BASE_DIR, "backend", "data", "sample_corpus.json")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

orchestrator = TruthGuardOrchestrator(corpus_path=CORPUS_PATH)

class TruthGuardRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _send_json_response(self, data: dict, status_code: int = 200):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/health":
            self._send_json_response({
                "status": "HEALTHY",
                "team": "CodeBots",
                "system": "TruthGuard Adversarial Multi-Agent Engine",
                "version": "1.2.0-Enterprise",
                "documents_indexed": len(orchestrator.vector_store.documents)
            })

        elif path == "/api/corpus":
            docs = list(orchestrator.vector_store.documents.values())
            self._send_json_response({
                "count": len(docs),
                "documents": docs
            })

        elif path == "/api/dag":
            self._send_json_response({
                "nodes": orchestrator.temporal_graph.nodes,
                "superseded_by_edges": orchestrator.temporal_graph.superseded_by_edges,
                "supersedes_edges": orchestrator.temporal_graph.supersedes_edges
            })

        elif path == "/api/benchmarks":
            benchmark_data = orchestrator.run_benchmark_suite()
            self._send_json_response(benchmark_data)

        else:
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8")
        try:
            body = json.loads(post_body) if post_body else {}
        except json.JSONDecodeError:
            self._send_json_response({"error": "Invalid JSON payload"}, 400)
            return

        if path == "/api/query":
            query = body.get("query", "").strip()
            top_k = int(body.get("top_k", 5))
            mode = body.get("mode", "dialectical")

            if not query:
                self._send_json_response({"error": "Query parameter cannot be empty"}, 400)
                return

            result = orchestrator.process_query(query=query, top_k=top_k, mode=mode)
            self._send_json_response(result)

        elif path == "/api/documents":
            doc = body.get("document")
            if not doc or "id" not in doc or "content" not in doc:
                self._send_json_response({"error": "Document requires id and content"}, 400)
                return

            orchestrator.temporal_graph.add_document(doc)
            orchestrator.vector_store.add_document(doc)
            self._send_json_response({
                "message": "Document successfully added to corpus and temporal graph.",
                "doc_id": doc["id"],
                "total_docs": len(orchestrator.vector_store.documents)
            })

        elif path == "/api/corpus/reset":
            count = orchestrator.reset_corpus()
            self._send_json_response({
                "message": "Corpus successfully reset to default benchmark documents.",
                "documents_indexed": count
            })

        else:
            self.send_error(404, "API endpoint not found")

def start_server(port: int = 8000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, TruthGuardRequestHandler)
    print(f"TruthGuard Multi-Agent Server running at http://127.0.0.1:{port}")
    print(f"Dashboard: http://127.0.0.1:{port}/index.html")
    print(f"Health API: http://127.0.0.1:{port}/api/health")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server cleanly.")
        httpd.server_close()

if __name__ == "__main__":
    start_server()
