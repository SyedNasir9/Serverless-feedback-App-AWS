import React from 'react';
import FeedbackForm from './components/FeedbackForm';
import FeedbackList from './components/FeedbackList';
import AnalyticsDashboard from './components/AnalyticsDashboard';

// API base
const API_BASE = process.env.REACT_APP_API_BASE || 'https://ho8ddocmdg.execute-api.ap-south-1.amazonaws.com/prod';

export const ENDPOINTS = {
  POST_FEEDBACK: API_BASE + '/feedback',
  GET_FEEDBACK: API_BASE + '/feedback',
  GET_ANALYTICS: API_BASE + '/analytics'
};

export default function App() {
  return (
    <div className="container py-5 fade-in">
      <h1 className="mb-4 text-center text-primary fw-bold">💬 Customer Feedback</h1>
      <div className="row g-4">
        <div className="col-md-6">
          <FeedbackForm />
          <AnalyticsDashboard />
        </div>
        <div className="col-md-6">
          <FeedbackList />
        </div>
      </div>
    </div>
  );
}
