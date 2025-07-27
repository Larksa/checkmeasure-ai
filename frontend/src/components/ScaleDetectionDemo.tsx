import React, { useState } from 'react';
import { Card, Button, Upload, message, Space, Spin, Typography, Input } from 'antd';
import { UploadOutlined, FileSearchOutlined, EditOutlined, CheckOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import AssumptionsDisplay, { Assumption } from './AssumptionsDisplay';
import api from '../utils/api';

const { Title, Text } = Typography;

interface AnalysisResult {
  scale: {
    scale_ratio: string;
    scale_factor: number;
    confidence: number;
    method: string;
    source_text?: string;
    page_number?: number;
  };
  joists: Array<{
    label: string;
    joist_type: string;
    sublabel?: string;
    dimensions?: any;
    material?: string;
    location?: any;
    confidence: number;
  }>;
  assumptions: Assumption[];
}

const ScaleDetectionDemo: React.FC = () => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [editingScale, setEditingScale] = useState(false);
  const [overrideScale, setOverrideScale] = useState('');

  const handleAnalyze = async () => {
    if (fileList.length === 0) {
      message.error('Please upload a PDF file first');
      return;
    }

    setAnalyzing(true);
    const file = fileList[0];

    try {
      const formData = new FormData();
      formData.append('file', file.originFileObj as Blob);
      if (overrideScale) {
        formData.append('override_scale', overrideScale);
      }

      const response = await api.post('/api/pdf/analyze-with-assumptions', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResults(response.data);
      message.success('Analysis complete!');
    } catch (error: any) {
      message.error(`Analysis failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleEditScale = (id: string) => {
    if (id === 'scale-1' && results) {
      setEditingScale(true);
      setOverrideScale(results.scale.scale_ratio);
    }
  };

  const handleSaveScale = () => {
    setEditingScale(false);
    // Re-analyze with new scale
    handleAnalyze();
  };

  const beforeUpload = (file: any) => {
    const isPDF = file.type === 'application/pdf';
    if (!isPDF) {
      message.error('You can only upload PDF files!');
      return false;
    }
    setFileList([file]);
    return false;
  };

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>
        <FileSearchOutlined /> Scale Detection & Assumptions Demo
      </Title>
      
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Upload
            beforeUpload={beforeUpload}
            fileList={fileList}
            onRemove={() => setFileList([])}
            maxCount={1}
          >
            <Button icon={<UploadOutlined />}>Select PDF</Button>
          </Upload>

          <Button 
            type="primary" 
            onClick={handleAnalyze}
            loading={analyzing}
            disabled={fileList.length === 0}
          >
            Analyze PDF
          </Button>
        </Space>
      </Card>

      {analyzing && (
        <Card style={{ textAlign: 'center', marginBottom: 16 }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>Analyzing PDF using hybrid approach...</Text>
          </div>
        </Card>
      )}

      {results && !analyzing && (
        <>
          {/* Scale Display */}
          <Card title="Detected Scale" style={{ marginBottom: 16 }}>
            <Space align="center">
              <Text style={{ fontSize: 24, fontWeight: 'bold' }}>
                {editingScale ? (
                  <Input
                    value={overrideScale}
                    onChange={(e) => setOverrideScale(e.target.value)}
                    style={{ width: 120 }}
                    placeholder="1:100"
                  />
                ) : (
                  results.scale.scale_ratio
                )}
              </Text>
              {editingScale ? (
                <Button 
                  type="primary" 
                  icon={<CheckOutlined />} 
                  onClick={handleSaveScale}
                >
                  Save
                </Button>
              ) : (
                <Button 
                  icon={<EditOutlined />} 
                  onClick={() => handleEditScale('scale-1')}
                >
                  Edit
                </Button>
              )}
            </Space>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                Method: {results.scale.method} | Confidence: {results.scale.confidence}%
              </Text>
            </div>
          </Card>

          {/* Assumptions Display */}
          <AssumptionsDisplay 
            assumptions={results.assumptions}
            onEdit={handleEditScale}
            minimal={false}
          />

          {/* Joists Found */}
          <Card title="Detected Joists" style={{ marginBottom: 16 }}>
            {results.joists.length > 0 ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                {results.joists.map((joist, index) => (
                  <div key={index} style={{ 
                    padding: 8, 
                    background: '#fafafa', 
                    borderRadius: 4 
                  }}>
                    <Text strong>{joist.label}</Text>
                    {joist.material && (
                      <Text type="secondary"> - {joist.material}</Text>
                    )}
                    {joist.dimensions && (
                      <Text type="secondary">
                        {' '}({joist.dimensions.width}x{joist.dimensions.height})
                      </Text>
                    )}
                  </div>
                ))}
              </Space>
            ) : (
              <Text type="secondary">No joists detected in this PDF</Text>
            )}
          </Card>
        </>
      )}
    </div>
  );
};

export default ScaleDetectionDemo;