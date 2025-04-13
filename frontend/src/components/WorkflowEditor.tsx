import React, { useState, useEffect, DragEvent, MouseEvent, ChangeEvent, ComponentType, useCallback, ReactNode, memo } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
  addEdge,
  Controls,
  Node,
  Edge,
  NodeProps,
  Position,
  XYPosition,
  Connection,
  EdgeChange,
  NodeChange,
  applyNodeChanges,
  applyEdgeChanges,
  NodeTypes,
  useReactFlow,
} from 'reactflow';
import { AgentTemplateList } from './AgentTemplateList';
import WorkflowResults from './WorkflowResults';

import 'reactflow/dist/style.css';

// --- Custom Node Components ---
// Wrapped with React.memo

const DefaultNodeComponent = memo(({ data }: NodeProps) => {
  return (
    <div style={{ padding: 10, border: '2px solid #777', borderRadius: 5, background: 'white', transition: 'all 0.3s, transform 0.3s' }}>
      <div>{data?.label || 'Default Node'}</div>
    </div>
  );
});

DefaultNodeComponent.displayName = 'DefaultNodeComponent';

const ParallelNodeComponent = memo(({ data }: NodeProps) => {
  return (
    <div style={{ padding: 10, border: '2px solid blue', borderRadius: 5, background: '#eef', transition: 'all 0.3s, transform 0.3s' }}>
      <div>{data?.label || 'Parallel Block'}</div>
    </div>
  );
});

ParallelNodeComponent.displayName = 'ParallelNodeComponent';

const DecisionNodeComponent = memo(({ data }: NodeProps) => {
  return (
    <div style={{ padding: 10, border: '2px solid green', borderRadius: 5, background: '#efe', transition: 'all 0.3s, transform 0.3s' }}>
      <div>{data?.label || 'Decision Point'}</div>
      <div style={{ fontSize: '0.8em', color: '#555' }}>Condition: {data?.condition || 'Not set'}</div>
    </div>
  );
});

DecisionNodeComponent.displayName = 'DecisionNodeComponent';


// --- Properties Panel Components ---

const NodePropertiesPanel: React.FC<{ node: Node; onUpdate: (data: any) => void }> = ({
  node,
  onUpdate,
}) => {
  const [properties, setProperties] = useState(node.data || {});

  useEffect(() => {
    setProperties(node.data || {});
  }, [node]);

  const handlePropertyChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setProperties((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    onUpdate(properties);
  };

  return (
    <div className="node-properties">
      <h4>Node: {properties.label || node.id}</h4>
      {Object.keys(properties).map((key) => (
        <div key={key} className="property-row" style={{ marginBottom: '8px' }}>
          <label htmlFor={`${node.id}-${key}`} style={{ display: 'block', marginBottom: '3px' }}>{key}:</label>
          <input
            type="text"
            id={`${node.id}-${key}`}
            name={key}
            value={properties[key] || ''}
            onChange={handlePropertyChange}
            style={{ width: '100%' }}
          />
        </div>
      ))}
      <button onClick={handleSave} style={{ marginTop: '10px' }}>Update Properties</button>
    </div>
  );
};

const ParallelNodePropertiesPanel: React.FC<{ node: Node; onUpdate: (data: any) => void }> = ({ node, onUpdate }) => {
   const [properties, setProperties] = useState(node.data || { label: 'Parallel Block' });

   useEffect(() => {
     setProperties(node.data || { label: 'Parallel Block' });
   }, [node]);

   const handlePropertyChange = (event: ChangeEvent<HTMLInputElement>) => {
     const { name, value } = event.target;
     setProperties((prev) => ({ ...prev, [name]: value }));
   };

   const handleSave = () => {
     onUpdate(properties);
   };

  return (
    <div>
      <h4>Parallel Block Properties</h4>
       <div style={{ marginBottom: '8px' }}>
         <label htmlFor={`${node.id}-label`} style={{ display: 'block', marginBottom: '3px' }}>Label:</label>
         <input
           type="text"
           id={`${node.id}-label`}
           name="label"
           value={properties.label || ''}
           onChange={handlePropertyChange}
           style={{ width: '100%' }}
         />
       </div>
       <button onClick={handleSave} style={{ marginTop: '10px' }}>Update Properties</button>
    </div>
  );
};

const DecisionNodePropertiesPanel: React.FC<{ node: Node; onUpdate: (data: any) => void }> = ({ node, onUpdate }) => {
  const [properties, setProperties] = useState(node.data || { label: 'Decision Point', condition: '' });

   useEffect(() => {
     setProperties(node.data || { label: 'Decision Point', condition: '' });
   }, [node]);

   const handlePropertyChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
     const { name, value } = event.target;
     setProperties((prev) => ({ ...prev, [name]: value }));
   };

    const handleSave = () => {
     onUpdate(properties);
   };

  return (
    <div>
      <h4>Decision Point Properties</h4>
       <div style={{ marginBottom: '8px' }}>
         <label htmlFor={`${node.id}-label`} style={{ display: 'block', marginBottom: '3px' }}>Label:</label>
         <input
           type="text"
           id={`${node.id}-label`}
           name="label"
           value={properties.label || ''}
           onChange={handlePropertyChange}
           style={{ width: '100%' }}
         />
       </div>
       <div style={{ marginBottom: '8px' }}>
         <label htmlFor={`${node.id}-condition`} style={{ display: 'block', marginBottom: '3px' }}>Condition:</label>
         <textarea
           id={`${node.id}-condition`}
           name="condition"
           value={properties.condition || ''}
           onChange={handlePropertyChange}
           style={{ width: '100%', minHeight: '60px' }}
           placeholder="e.g., context.variable > 10"
         />
       </div>
       <button onClick={handleSave} style={{ marginTop: '10px' }}>Update Properties</button>
    </div>
  );
};


// --- Main Workflow Editor Component ---

const WorkflowEditorInternal: React.FC = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [workflowId, setWorkflowId] = useState<string>('1');
  const [showResults, setShowResults] = useState<boolean>(false);
  const reactFlowInstance = useReactFlow();

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  useEffect(() => {
    fetchWorkflowData();
  }, [workflowId]);

  const fetchWorkflowData = async () => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const workflowData = await response.json();
      setNodes(workflowData.nodes || []);
      setEdges(workflowData.edges || []);
      setTimeout(() => reactFlowInstance.fitView(), 0);
    } catch (error) {
      console.error('Error fetching workflow data:', error);
      setNodes([]);
      setEdges([]);
    }
  };

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onDragOver = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      if (typeof type === 'undefined' || !type) return;

      const position = reactFlowInstance.project({
        x: event.clientX - (event.target as HTMLElement).getBoundingClientRect().left,
        y: event.clientY - (event.target as HTMLElement).getBoundingClientRect().top,
      });

      let newNode: Node;
      const newNodeId = `${type}-${+new Date()}`;

      if (type === 'parallel') {
        newNode = { id: newNodeId, type, position, data: { label: 'Parallel Execution' } };
      } else if (type === 'decision') {
        newNode = { id: newNodeId, type, position, data: { label: 'Decision Point', condition: '' } };
      } else {
        newNode = { id: newNodeId, type: 'default', position, data: { label: `${type} Node` } };
      }

      setNodes((nds) => [...nds, newNode]);
    },
    [reactFlowInstance, setNodes]
  );

  const onNodeClick = useCallback((event: MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const updateNodeProperties = useCallback((updatedData: any) => {
    if (!selectedNode) return;
    setNodes((nds) =>
      nds.map((n) =>
        n.id === selectedNode.id ? { ...n, data: { ...n.data, ...updatedData } } : n
      )
    );
    setSelectedNode((prev) => prev ? { ...prev, data: { ...prev.data, ...updatedData } } : null);
  }, [selectedNode, setNodes]);


  const saveWorkflow = async () => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes: reactFlowInstance.getNodes(), edges: reactFlowInstance.getEdges() }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      console.log('Workflow saved:', data.message);
    } catch (error) {
      console.error('Error saving workflow:', error);
    }
  };

  const executeWorkflow = async () => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}/execute`, { method: 'POST' });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      console.log('Workflow execution:', data.message);
      
      // Показываем панель результатов после выполнения
      setShowResults(true);
    } catch (error) {
      console.error('Error executing workflow:', error);
    }
  };

  const generateWorkflow = async () => {
    try {
      // Запрос к API для генерации рабочего процесса
      const response = await fetch('/api/workflows/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project_brief: 'Example project brief' }),
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const workflowData = await response.json();
      setNodes(workflowData.nodes || []);
      setEdges(workflowData.edges || []);
      setTimeout(() => reactFlowInstance.fitView(), 0);
      console.log('Workflow generated successfully');
    } catch (error) {
      console.error('Error generating workflow:', error);
    }
  };

  const handleDragStart = (event: DragEvent<HTMLDivElement>, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  // Define node types using the memoized components, casting to any as a workaround
  const nodeTypes: NodeTypes = {
     default: DefaultNodeComponent as any, // Cast to any
     parallel: ParallelNodeComponent as any, // Cast to any
     decision: DecisionNodeComponent as any, // Cast to any
  };

  return (
      <div className="workflow-editor" style={{ display: 'flex', height: '100vh' }}>
        <div className="sidebar" style={{ width: '200px', borderRight: '1px solid #ccc', padding: '10px', background: '#f7f7f7' }}>
          <AgentTemplateList onDragStart={handleDragStart} />
          <button onClick={generateWorkflow} style={{ marginTop: '10px', width: '100%' }}>Generate Workflow</button>
        </div>
        <div className="workflow-canvas" style={{ flexGrow: 1 }} >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            onDrop={onDrop}
            onDragOver={onDragOver}
            fitView
          >
            <Controls />
          </ReactFlow>
        </div>
        {selectedNode && (
          <div className="node-properties-panel" style={{ width: '250px', borderLeft: '1px solid #ccc', padding: '10px', background: '#f7f7f7' }}>
            {selectedNode.type === 'parallel' && <ParallelNodePropertiesPanel node={selectedNode} onUpdate={updateNodeProperties} />}
            {selectedNode.type === 'decision' && <DecisionNodePropertiesPanel node={selectedNode} onUpdate={updateNodeProperties} />}
            {(!selectedNode.type || selectedNode.type === 'default') && <NodePropertiesPanel node={selectedNode} onUpdate={updateNodeProperties} />}
          </div>
        )}
        <div className="workflow-actions" style={{ position: 'absolute', top: '10px', right: '10px', zIndex: 4 }}>
          <button onClick={saveWorkflow} style={{ marginRight: '5px' }}>Save</button>
          <button onClick={executeWorkflow} style={{ marginRight: '5px' }}>Execute</button>
          <button
            onClick={() => setShowResults(!showResults)}
            style={{
              backgroundColor: showResults ? '#e0e0e0' : 'white',
              fontWeight: showResults ? 'bold' : 'normal'
            }}
          >
            {showResults ? 'Hide Results' : 'Show Results'}
          </button>
        </div>
        
        {showResults && (
          <div className="workflow-results-panel" style={{
            position: 'absolute',
            bottom: '10px',
            right: '10px',
            width: '400px',
            height: '300px',
            background: 'white',
            border: '1px solid #ccc',
            borderRadius: '5px',
            padding: '10px',
            boxShadow: '0 0 10px rgba(0,0,0,0.1)',
            zIndex: 5,
            overflow: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <h3 style={{ margin: 0 }}>Execution Results</h3>
              <button onClick={() => setShowResults(false)} style={{ border: 'none', background: 'none', cursor: 'pointer' }}>✕</button>
            </div>
            <WorkflowResults workflowId={workflowId} />
          </div>
        )}
      </div>
  );
};

const WorkflowEditor: React.FC = () => (
  <ReactFlowProvider>
    <WorkflowEditorInternal />
  </ReactFlowProvider>
);


export default WorkflowEditor;
