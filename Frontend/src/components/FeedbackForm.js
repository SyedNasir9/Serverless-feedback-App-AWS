import React, { useState } from "react";
import { ENDPOINTS } from "../App";

export default function FeedbackForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [rating, setRating] = useState(5);
  const [busy, setBusy] = useState(false);
  const [ok, setOk] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);

    try {
      const res = await fetch(ENDPOINTS.POST_FEEDBACK, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, message, rating }),
      });

      if (res.status === 201) {
        setOk(true);
        setName(""); setEmail(""); setMessage(""); setRating(5);
      } else {
        setOk(false);
      }
    } catch (err) {
      console.error("Error submitting feedback:", err);
      setOk(false);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card shadow-lg border-0 rounded-3 mb-4 fade-in" style={{ background: "#ffffff" }}>
      <div className="card-body">
        <h5 className="card-title text-primary mb-3">📝 Leave Your Feedback</h5>

        <form onSubmit={submit}>
          <div className="mb-3">
            <label className="form-label text-muted">Name</label>
            <input
              className="form-control"
              placeholder="Your name (optional)"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="mb-3">
            <label className="form-label text-muted">Email</label>
            <input
              className="form-control"
              type="email"
              placeholder="Email (optional)"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="mb-3">
            <label className="form-label text-muted">Feedback</label>
            <textarea
              className="form-control"
              rows="3"
              placeholder="Write your feedback here..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label text-muted me-2">Rating</label>
            <select
              className="form-select w-auto d-inline-block"
              value={rating}
              onChange={(e) => setRating(e.target.value)}
            >
              {[5, 4, 3, 2, 1].map((r) => (
                <option key={r} value={r}>{"⭐".repeat(r)} ({r})</option>
              ))}
            </select>
          </div>

          <button className="btn btn-primary w-100" disabled={busy}>
            {busy ? "⏳ Sending..." : "📤 Send Feedback"}
          </button>

          {ok === true && <div className="mt-3 alert alert-success mb-0">✅ Thanks for your feedback!</div>}
          {ok === false && <div className="mt-3 alert alert-danger mb-0">❌ Something went wrong. Please try again.</div>}
        </form>
      </div>
    </div>
  );
}
