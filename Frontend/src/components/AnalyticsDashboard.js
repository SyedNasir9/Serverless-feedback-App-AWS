import React, { useEffect, useState } from "react";
import { ENDPOINTS } from "../App";

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState({});

  useEffect(() => { fetchMetrics(); }, []);

  async function fetchMetrics() {
    try {
      const res = await fetch(ENDPOINTS.GET_ANALYTICS);
      const j = await res.json();
      setMetrics(j);
    } catch (e) {
      console.error("Error fetching analytics:", e);
    }
  }

  const total = metrics.total_feedbacks || 0;
  const positive = metrics.positive_count || 0;
  const neutral = metrics.neutral_count || 0;
  const negative = metrics.negative_count || 0;

  const positivePct = total ? ((positive / total) * 100).toFixed(1) : 0;
  const neutralPct = total ? ((neutral / total) * 100).toFixed(1) : 0;
  const negativePct = total ? ((negative / total) * 100).toFixed(1) : 0;

  return (
    <div className="card mt-4 shadow-lg border-0 rounded-3 fade-in" style={{ background: "#ffffff" }}>
      <div className="card-body">
        <h5 className="card-title text-primary mb-3">📊 Analytics Overview</h5>

        <div className="mb-3">
          <h6 className="text-muted">Total Feedbacks</h6>
          <p className="fs-4 fw-bold text-dark">{total}</p>
        </div>

        <div className="mb-3">
          <h6 className="text-muted">Average Rating</h6>
          <p className="fs-4 fw-bold text-warning">⭐ {metrics.avg_rating ? metrics.avg_rating.toFixed(2) : 0}</p>
        </div>

        <div className="mb-2">
          <h6 className="text-muted">Sentiment Breakdown</h6>

          <div className="mb-2">
            <span className="fw-bold text-success">😊 Positive: {positive}</span>
            <div className="progress mt-1"><div className="progress-bar bg-success" style={{ width: `${positivePct}%` }}></div></div>
          </div>

          <div className="mb-2">
            <span className="fw-bold text-secondary">😐 Neutral: {neutral}</span>
            <div className="progress mt-1"><div className="progress-bar bg-secondary" style={{ width: `${neutralPct}%` }}></div></div>
          </div>

          <div className="mb-2">
            <span className="fw-bold text-danger">😡 Negative: {negative}</span>
            <div className="progress mt-1"><div className="progress-bar bg-danger" style={{ width: `${negativePct}%` }}></div></div>
          </div>
        </div>
      </div>
    </div>
  );
}
