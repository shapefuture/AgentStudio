import React, { useState, useEffect, useMemo } from 'react';
import ReactFlow, { useNodesState, useEdgesState, addEdge, Controls } from 'reactflow';
import AgentTemplateList from './AgentTemplateList';
import { toast } from 'react-toastify';
import 'reactflow/dist/style.css';

// Определяем nodeTypes вне компонента, чтобы избежать предупреждения
const defaultNodeTypes = {
  default: 'default',
};

const WorkflowEditor = () => {
  // Используем useMemo для мемоизации nodeTypes
  const nodeTypes = useMemo(() => defaultNodeTypes, []);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [workflowId, setWorkflowId] = useState('1');

  useEffect(() => {
    // Fetch initial workflow data from backend API
    fetchWorkflowData();
  }, []);

  const fetchWorkflowData = async () => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          // Если рабочий процесс не найден, создаем пустой
          console.log('Workflow not found, creating empty workflow');
          setNodes([]);
          setEdges([]);
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const workflowData = await response.json();
      setNodes(workflowData.nodes || []);
      setEdges(workflowData.edges || []);
    } catch (error) {
      console.error('Error fetching workflow data:', error);
      toast.error('Failed to load workflow data');
      // Устанавливаем пустые узлы и ребра в случае ошибки
      setNodes([]);
      setEdges([]);
    }
  };

  const onConnect = (params) => setEdges((eds) => addEdge(params, eds));

  const onDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const onDrop = (event) => {
    event.preventDefault();

    const type = event.dataTransfer.getData('application/reactflow');
    const position = { x: event.clientX, y: event.clientY - 40 };
    const newNode = { id: `${type}-${nodes.length + 1}`, type, position };

    setNodes((nds) => [...nds, newNode]);
  };

  const onNodeClick = (event, node) => {
    setSelectedNode(node);
  };

  const updateNodeProperties = (updatedNode) => {
    setNodes((nds) =>
      nds.map((n) => (n.id === updatedNode.id ? { ...n, ...updatedNode } : n))
    );
  };

  const saveWorkflow = async () => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nodes, edges }),
      });
      const data = await response.json();
      console.log(data.message);
    } catch (error) {
      console.error('Error saving workflow:', error);
    }
  };

  const executeWorkflow = async () => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}/execute`, {
        method: 'POST',
      });
      const data = await response.json();
      console.log(data.message);
    } catch (error) {
      console.error('Error executing workflow:', error);
    }
  };

  const generateWorkflow = async () => {
    try {
      // Используем API для генерации рабочего процесса
      const response = await fetch('/api/workflows/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_brief: 'Example project brief',
          use_llm: true // Используем LLM для генерации, если доступно
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Устанавливаем ID нового рабочего процесса
      setWorkflowId(data.workflow_id);
      
      // Устанавливаем узлы и ребра
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
      
      toast.success('Workflow generated successfully');
    } catch (error) {
      console.error('Error generating workflow:', error);
      toast.error('Failed to generate workflow');
    }
  }

  return (
    <div className="workflow-editor">
      <div className="sidebar">
        <AgentTemplateList onDragStart={onDragStart} />
        <button onClick={generateWorkflow}>Generate Workflow</button>
      </div>
      <div className="workflow-canvas" onDragOver={onDragOver} onDrop={onDrop}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
        >
          <Controls />
        </ReactFlow>
      </div>
      {selectedNode && (
        <div className="node-properties-panel" style={{ padding: '10px', border: '1px solid #ccc', marginLeft: '10px' }}>
          <h3>Node Properties</h3>
          <div>
            <p><strong>ID:</strong> {selectedNode.id}</p>
            <p><strong>Type:</strong> {selectedNode.type || 'default'}</p>
            {selectedNode.data && Object.entries(selectedNode.data).map(([key, value]) => (
              <div key={key} style={{ marginBottom: '10px' }}>
                <label htmlFor={key} style={{ display: 'block', marginBottom: '5px' }}>{key}:</label>
                <input
                  type="text"
                  id={key}
                  value={value || ''}
                  onChange={(e) => {
                    const updatedData = { ...selectedNode.data, [key]: e.target.value };
                    updateNodeProperties({ ...selectedNode, data: updatedData });
                  }}
                  style={{ width: '100%', padding: '5px' }}
                />
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="workflow-actions">
        <button onClick={saveWorkflow}>Save Workflow</button>
        <button onClick={executeWorkflow}>Execute Workflow</button>
      </div>
    </div>
  );
};

export default WorkflowEditor;