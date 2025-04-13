import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';

// Определение API URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '';

// Типы данных
interface WorkflowResult {
  id: string;
  workflow_id: string;
  timestamp: string;
  status: 'running' | 'completed' | 'failed' | 'queued';
  data: any;
}

interface WorkflowResultsProps {
  workflowId: string;
  limit?: number;
  autoRefresh?: boolean;
}

interface TaskResult {
  status: string;
  result?: any;
  error?: string;
  execution_time?: number;
}

// Компонент для отображения результатов выполнения рабочего процесса
const WorkflowResults: React.FC<WorkflowResultsProps> = ({
  workflowId,
  limit = 5,
  autoRefresh = true
}) => {
  const [results, setResults] = useState<WorkflowResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(0);
  const [totalResults, setTotalResults] = useState<number>(0);
  const [selectedResult, setSelectedResult] = useState<WorkflowResult | null>(null);
  const [showDetails, setShowDetails] = useState<boolean>(false);

  // Функция для загрузки результатов
  const fetchResults = useCallback(async () => {
    if (!workflowId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const offset = page * limit;
      const response = await fetch(
        `${API_BASE_URL}/api/workflows/${workflowId}/results?limit=${limit}&offset=${offset}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setResults(data.results || []);
      setTotalResults(data.total || 0);
    } catch (error) {
      console.error('Error fetching workflow results:', error);
      setError('Failed to fetch workflow results. Please try again.');
      toast.error('Failed to load execution results');
    } finally {
      setLoading(false);
    }
  }, [workflowId, page, limit]);

  // Загрузка результатов при изменении workflowId или страницы
  useEffect(() => {
    fetchResults();
    
    // Настраиваем интервал для периодического обновления результатов
    let intervalId: number | undefined;
    
    if (autoRefresh) {
      intervalId = window.setInterval(fetchResults, 5000);
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [workflowId, page, fetchResults, autoRefresh]);

  // Функция для загрузки деталей результата
  const fetchResultDetails = useCallback(async (executionId: string) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/workflows/${workflowId}/results/${executionId}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setSelectedResult(data);
      setShowDetails(true);
    } catch (error) {
      console.error('Error fetching result details:', error);
      toast.error('Failed to load execution details');
    }
  }, [workflowId]);

  // Функция для отображения деталей задачи
  const renderTaskResults = (taskResults: Record<string, TaskResult>) => {
    if (!taskResults || Object.keys(taskResults).length === 0) {
      return <p>No task results available</p>;
    }
    
    return (
      <div className="task-results" style={{ marginBottom: '20px' }}>
        <h4>Task Results</h4>
        {Object.entries(taskResults).map(([taskId, result]) => (
          <div
            key={taskId}
            style={{
              padding: '8px',
              margin: '5px 0',
              borderRadius: '4px',
              backgroundColor: result.status === 'success' ? '#e6f7e6' : '#ffebee',
              border: `1px solid ${result.status === 'success' ? '#a5d6a7' : '#ef9a9a'}`
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <strong>{taskId}</strong>
              <span style={{
                fontWeight: 'bold',
                color: result.status === 'success' ? '#2e7d32' : '#c62828'
              }}>
                {result.status.toUpperCase()}
              </span>
            </div>
            
            {result.execution_time && (
              <div style={{ fontSize: '0.8em', color: '#666' }}>
                Execution time: {result.execution_time.toFixed(2)}s
              </div>
            )}
            
            {result.result && (
              <div style={{ marginTop: '5px' }}>
                <details>
                  <summary>Result</summary>
                  <pre style={{
                    backgroundColor: '#f5f5f5',
                    padding: '8px',
                    borderRadius: '4px',
                    overflow: 'auto',
                    maxHeight: '150px',
                    fontSize: '0.8em'
                  }}>
                    {typeof result.result === 'object'
                      ? JSON.stringify(result.result, null, 2)
                      : String(result.result)}
                  </pre>
                </details>
              </div>
            )}
            
            {result.error && (
              <div style={{ marginTop: '5px', color: '#c62828' }}>
                <strong>Error:</strong> {result.error}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  // Компонент для отображения деталей результата
  const ResultDetails = () => {
    if (!selectedResult) return null;
    
    return (
      <div
        className="result-details-modal"
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '80%',
          maxWidth: '800px',
          maxHeight: '80vh',
          overflowY: 'auto',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          padding: '20px',
          zIndex: 1000
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3 style={{ margin: 0 }}>Execution Details</h3>
          <button
            onClick={() => setShowDetails(false)}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5em',
              cursor: 'pointer'
            }}
          >
            ✕
          </button>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <p><strong>Execution ID:</strong> {selectedResult.id}</p>
          <p><strong>Status:</strong> <span style={{
            fontWeight: 'bold',
            color: selectedResult.status === 'completed' ? '#2e7d32' :
                  selectedResult.status === 'failed' ? '#c62828' : '#1565c0'
          }}>
            {selectedResult.status.toUpperCase()}
          </span></p>
          <p><strong>Timestamp:</strong> {new Date(selectedResult.timestamp).toLocaleString()}</p>
        </div>
        
        {selectedResult.data && selectedResult.data.results && (
          renderTaskResults(selectedResult.data.results)
        )}
        
        <div style={{ marginTop: '15px' }}>
          <h4>Raw Data</h4>
          <pre style={{
            backgroundColor: '#f5f5f5',
            padding: '10px',
            borderRadius: '4px',
            overflow: 'auto',
            maxHeight: '300px'
          }}>
            {JSON.stringify(selectedResult.data, null, 2)}
          </pre>
        </div>
      </div>
    );
  };

  // Отображение состояния загрузки
  if (loading && results.length === 0) {
    return (
      <div className="workflow-results-loading" style={{ textAlign: 'center', padding: '20px' }}>
        <div className="loading-spinner" style={{
          display: 'inline-block',
          width: '30px',
          height: '30px',
          border: '3px solid rgba(0,0,0,0.1)',
          borderRadius: '50%',
          borderTop: '3px solid #3498db',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p>Loading results...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Отображение ошибки
  if (error && results.length === 0) {
    return (
      <div className="workflow-results-error" style={{
        padding: '15px',
        backgroundColor: '#ffebee',
        color: '#c62828',
        borderRadius: '4px',
        marginBottom: '10px'
      }}>
        <p>{error}</p>
        <button
          onClick={fetchResults}
          style={{
            padding: '5px 10px',
            backgroundColor: '#f0f0f0',
            border: '1px solid #ccc',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  // Отображение пустого состояния
  if (results.length === 0) {
    return (
      <div className="workflow-results-empty" style={{
        padding: '15px',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px',
        textAlign: 'center'
      }}>
        <p>No results available for this workflow.</p>
        <p>Execute the workflow to see results here.</p>
      </div>
    );
  }

  // Основной компонент
  return (
    <div className="workflow-results">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h3 style={{ margin: 0 }}>Execution Results</h3>
        <button
          onClick={fetchResults}
          style={{
            padding: '5px 10px',
            backgroundColor: '#f0f0f0',
            border: '1px solid #ccc',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      
      <div className="results-list">
        {results.map((result) => (
          <div
            key={result.id}
            className={`result-item result-${result.status}`}
            style={{
              padding: '10px',
              margin: '5px 0',
              borderRadius: '4px',
              backgroundColor: result.status === 'completed' ? '#e6f7e6' :
                              result.status === 'failed' ? '#ffebee' :
                              result.status === 'queued' ? '#fff8e1' : '#e3f2fd',
              border: `1px solid ${result.status === 'completed' ? '#a5d6a7' :
                                  result.status === 'failed' ? '#ef9a9a' :
                                  result.status === 'queued' ? '#ffe082' : '#90caf9'}`,
              cursor: 'pointer'
            }}
            onClick={() => fetchResultDetails(result.id)}
          >
            <div className="result-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="result-timestamp">{new Date(result.timestamp).toLocaleString()}</span>
              <span className="result-status" style={{
                fontWeight: 'bold',
                color: result.status === 'completed' ? '#2e7d32' :
                       result.status === 'failed' ? '#c62828' :
                       result.status === 'queued' ? '#f57f17' : '#1565c0'
              }}>
                {result.status.toUpperCase()}
              </span>
            </div>
            
            <div className="result-summary" style={{ marginTop: '5px', fontSize: '0.9em' }}>
              {result.data && result.data.message && (
                <div>{result.data.message}</div>
              )}
              
              {result.data && result.data.tasks_completed && (
                <div>Tasks completed: {result.data.tasks_completed}</div>
              )}
              
              {result.data && result.data.error && (
                <div style={{ color: '#c62828' }}>Error: {result.data.error}</div>
              )}
              
              <div style={{ textAlign: 'right', fontSize: '0.8em', color: '#666', marginTop: '5px' }}>
                Click for details
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Пагинация */}
      {totalResults > limit && (
        <div className="pagination" style={{
          display: 'flex',
          justifyContent: 'center',
          marginTop: '15px'
        }}>
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            style={{
              padding: '5px 10px',
              backgroundColor: page === 0 ? '#f0f0f0' : 'white',
              border: '1px solid #ccc',
              borderRadius: '4px 0 0 4px',
              cursor: page === 0 ? 'default' : 'pointer',
              opacity: page === 0 ? 0.6 : 1
            }}
          >
            Previous
          </button>
            <div style={{
              padding: '10px',
              margin: '5px 0',
              borderRadius: '4px',
              backgroundColor: result.status === 'success' ? '#e6f7e6' : '#ffebee',
              border: `1px solid ${result.status === 'success' ? '#a5d6a7' : '#ef9a9a'}`,
              transition: 'background-color 0.3s',
              cursor: 'pointer'
            }} onClick={() => fetchResultDetails(taskId)}>

            Page {page + 1} of {Math.ceil(totalResults / limit)}
          </div>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={(page + 1) * limit >= totalResults}
            style={{
              padding: '5px 10px',
              backgroundColor: (page + 1) * limit >= totalResults ? '#f0f0f0' : 'white',
              border: '1px solid #ccc',
              borderRadius: '0 4px 4px 0',
              cursor: (page + 1) * limit >= totalResults ? 'default' : 'pointer',
              opacity: (page + 1) * limit >= totalResults ? 0.6 : 1
            }}
          >
            Next
          </button>
        </div>
      )}
      
      {/* Модальное окно с деталями */}
      {showDetails && <ResultDetails />}
      
      {/* Затемнение фона при открытии модального окна */}
      {showDetails && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 999
          }}
          onClick={() => setShowDetails(false)}
        />
      )}
    </div>
  );
};

export default WorkflowResults;
