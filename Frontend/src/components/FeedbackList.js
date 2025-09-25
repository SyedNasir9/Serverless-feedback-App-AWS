import React, { useState, useEffect } from "react";
import { ENDPOINTS } from "../App";

export default function FeedbackList() {
  const [items, setItems] = useState([]);

  useEffect(() => { fetchList(); }, []);

  async function fetchList() {
    try {
      const res = await fetch(ENDPOINTS.GET_FEEDBACK);
      const j = await res.json();
      setItems(j.items || []);
    } catch (e) {
      console.error("Error fetching feedback:", e);
    }
  }

  return (
    <div className="fade-in">
      <h5 className="mb-3 text-primary">🗂 Recent Feedback</h5>

      <div className="list-group">
        {items.length === 0 && <div className="list-group-item text-muted text-center">No feedback yet.</div>}

        {items.map((it) => (
          <div key={it.feedback_id} className="list-group-item mb-2 rounded-3 shadow-sm">
            <div className="d-flex justify-content-between align-items-center">
              <div><strong>{it.name || "Anonymous"}</strong></div>
              <div>⭐ {it.rating} • {it.sentiment}</div>
            </div>
            <div className="small text-muted">{new Date(it.created_at * 1000).toLocaleString()}</div>
            <p className="mb-0 mt-2">{it.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
