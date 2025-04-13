import React, { DragEvent } from 'react';

interface AgentTemplate {
  id: string;
  type: string;
  name: string;
  description: string;
  color: string;
  backgroundColor: string;
}

interface AgentTemplateListProps {
  onDragStart: (event: DragEvent<HTMLDivElement>, nodeType: string) => void;
}

export const AgentTemplateList: React.FC<AgentTemplateListProps> = ({ onDragStart }) => {
  const agentTemplates: AgentTemplate[] = [
    {
      id: 'default',
      type: 'default',
      name: 'Default Agent',
      description: 'A general-purpose agent for basic tasks',
      color: '#777',
      backgroundColor: 'white',
    },
    {
      id: 'parallel',
      type: 'parallel',
      name: 'Parallel Block',
      description: 'Execute multiple tasks concurrently',
      color: 'blue',
      backgroundColor: '#eef',
    },
    {
      id: 'decision',
      type: 'decision',
      name: 'Decision Point',
      description: 'Branch workflow based on conditions',
      color: 'green',
      backgroundColor: '#efe',
    },
    {
      id: 'market_analyst',
      type: 'default',
      name: 'Market Analyst',
      description: 'Analyzes market trends and opportunities',
      color: '#d35400',
      backgroundColor: '#ffeee5',
    },
    {
      id: 'content_generator',
      type: 'default',
      name: 'Content Generator',
      description: 'Creates marketing content and copy',
      color: '#8e44ad',
      backgroundColor: '#f5eeff',
    },
  ];

  return (
    <div className="agent-template-list">
      <p><strong>Agent Templates</strong></p>
      {agentTemplates.map((template) => (
        <div
          key={template.id}
          onDragStart={(event) => onDragStart(event, template.type)}
          draggable
          style={{
            border: `1px solid ${template.color}`,
            padding: '16px',
            marginBottom: '12px',
            cursor: 'grab',
            background: template.backgroundColor,
            borderRadius: '8px',
            boxShadow: '0 2px 5px rgba(0, 0, 0, 0.2)',
            display: 'flex',
            alignItems: 'center',
          }}
          title={template.description}
        >
          <img src={`path/to/icons/${template.type}.svg`} alt={`${template.name} icon`} style={{ width: '24px', height: '24px', marginRight: '8px' }} />
          <span>{template.name}</span>
        </div>
      ))}
    </div>
  );
};

export default AgentTemplateList;
