import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const WorkflowMonitor = ({ workflowId }) => {
  const [status, setStatus] = useState(null);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/api/workflows/${workflowId}/monitor`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStatus(data);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setSocket(null);
    };

    return () => {
      if (ws) ws.close();
    };
  }, [workflowId]);

  if (!status) return <div>Loading workflow status...</div>;

  return (
    <div className="workflow-monitor">
      <h3>Workflow Monitor: {workflowId}</h3>
      <div className="status-section">
        <h4>Current Status</h4>
        <p>State: {status.status}</p>
        {status.current_node && <p>Current Node: {status.current_node}</p>}
        {status.progress && (
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${status.progress}%` }}
            ></div>
          </div>
        )}
      </div>
      <div className="history-section">
        <h4>Execution History</h4>
        {status.history?.steps?.map((step, index) => (
          <div key={index} className="history-step">
            <p>Step {index + 1}: {step.node}</p>
            <p>Status: {step.status}</p>
            <p>Duration: {step.duration}ms</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowMonitor;
