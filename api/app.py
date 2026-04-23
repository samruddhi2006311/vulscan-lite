import sys
import os
import ssl as ssl_lib

# Add root folder to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
from dotenv import load_dotenv

# Load env variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Redis / Celery config ──────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL")

ssl_settings = {"ssl_cert_reqs": ssl_lib.CERT_NONE}

celery = Celery(app.name, broker=REDIS_URL, backend=REDIS_URL)
celery.conf.update(
    broker_use_ssl=ssl_settings,
    redis_backend_use_ssl=ssl_settings,
    broker_transport_options={"visibility_timeout": 3600},
    broker_pool_limit=0,
    broker_heartbeat=None,
    result_expires=3600
)


# ── Celery Task ────────────────────────────────────────────
@celery.task(bind=True)
def scan_task(self, url):
    # Force load env variables inside worker process
    from dotenv import load_dotenv as _load
    import os as _os
    _load(_os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
        '.env'
    ))

    from scanner.header_check import check_headers
    from scanner.ssl_check import check_ssl
    from scanner.cms_check import check_cms

    header_result = check_headers(url)
    ssl_result    = check_ssl(url)
    cms_result    = check_cms(url)

    total_score = header_result["score"]
    if ssl_result["is_valid"]:
        total_score += 30
    else:
        total_score -= 30

    if total_score >= 30:
        grade = "A"
    elif total_score >= 10:
        grade = "B"
    elif total_score >= 0:
        grade = "C"
    else:
        grade = "D"

    result = {
        "url": url,
        "total_score": total_score,
        "grade": grade,
        "headers": header_result,
        "ssl": ssl_result,
        "cms": cms_result
    }

    # Save to Supabase database
    try:
        from api.database import save_scan
        save_scan(self.request.id, result)
        print(f"✅ Scan saved to database: {url}")
    except Exception as e:
        print(f"❌ Database save error: {e}")

    return result


# ── POST /api/scan ─────────────────────────────────────────
@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Please provide a URL"}), 400

    url = data["url"]
    task = scan_task.delay(url)

    return jsonify({
        "job_id": task.id,
        "status": "pending",
        "message": "Scan started! Poll /api/scan/status/<job_id> for results"
    }), 202


# ── GET /api/scan/status/<job_id> ──────────────────────────
@app.route("/api/scan/status/<job_id>", methods=["GET"])
def scan_status(job_id):
    task = scan_task.AsyncResult(job_id)

    if task.state == "PENDING":
        return jsonify({"status": "pending"}), 200
    elif task.state == "SUCCESS":
        return jsonify({"status": "completed", "result": task.result}), 200
    elif task.state == "FAILURE":
        return jsonify({"status": "failed", "error": str(task.info)}), 500

    return jsonify({"status": task.state}), 200


# ── GET /api/scan/pdf/<job_id> ─────────────────────────────
@app.route("/api/scan/pdf/<job_id>", methods=["GET"])
def download_pdf(job_id):
    from scanner.pdf_generator import generate_pdf
    from flask import send_file
    import io

    task = scan_task.AsyncResult(job_id)
    if task.state != "SUCCESS":
        return jsonify({"error": "Scan not completed yet"}), 400

    pdf_bytes = generate_pdf(task.result)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'vulnscan-report-{job_id[:8]}.pdf'
    )


# ── GET /api/history ───────────────────────────────────────
@app.route("/api/history", methods=["GET"])
def scan_history():
    try:
        from api.database import get_history
        history = get_history()
        return jsonify(history), 200
    except Exception as e:
        print(f"❌ History endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


# ── DELETE /api/history ────────────────────────────────────
@app.route("/api/history", methods=["DELETE"])
def clear_history():
    try:
        from api.database import delete_history
        delete_history()
        return jsonify({"message": "History cleared"}), 200
    except Exception as e:
        print(f"❌ Clear history error: {e}")
        return jsonify({"error": str(e)}), 500


# ── GET / ──────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "VulnScan Lite API is running!"}), 200


# ── Start Celery worker in background thread ───────────────
import threading

def start_celery():
    import subprocess
    subprocess.run([
        sys.executable, '-m', 'celery',
        '-A', 'api.app.celery',
        'worker',
        '--loglevel=info',
        '--pool=solo',
        '--concurrency=1'
    ])

celery_thread = threading.Thread(target=start_celery, daemon=True)
celery_thread.start()


if __name__ == "__main__":
    app.run(debug=True, port=5000)