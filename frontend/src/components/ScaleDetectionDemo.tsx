import React, { useState } from 'react';
import { Card, Button, Upload, message, Space, Spin, Typography, Input } from 'antd';
import { UploadOutlined, FileSearchOutlined, EditOutlined, CheckOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import AssumptionsDisplay, { Assumption } from './AssumptionsDisplay';
import PDFWithMeasurements from './ScaleDetectionDemo/PDFWithMeasurements';
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
  joist_patterns?: Array<{
    label: string;
    bounding_box: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    orientation: string;
    confidence: number;
    characteristics: string;
    nearby_text?: string;
  }>;
  joist_measurements?: Array<{
    pattern_label: string;
    horizontal_span_m: number;
    vertical_span_m?: number;
    joist_count: number;
    confidence: number;
    measurement_method: string;
    line_details?: any;
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
      console.log('File object:', file);
      console.log('originFileObj:', file.originFileObj);
      formData.append('file', file as any as File);
      if (overrideScale) {
        formData.append('override_scale', overrideScale);
      }
      
      // Debug FormData contents
      console.log('FormData entries:');
      Array.from(formData.entries()).forEach(([key, value]) => {
        console.log(key, value);
      });

      const response = await api.post('/api/pdf/analyze-with-assumptions', formData, {
        headers: {
          'Content-Type': undefined  // Override default application/json
        }
      });

      setResults(response.data);
      message.success('Analysis complete!');
    } catch (error: any) {
      console.error('Full error response:', error.response);
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
            <Text>Analyzing PDF using Claude Vision AI...</Text>
            <br />
            <Text type="secondary" style={{ fontSize: 12 }}>
              This may take up to 90 seconds for complex drawings
            </Text>
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

          {/* Detected Patterns */}
          {results.joist_patterns && results.joist_patterns.length > 0 && (
            <Card title="Detected Patterns" style={{ marginBottom: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                {results.joist_patterns.map((pattern, index) => (
                  <div key={index} style={{ 
                    padding: 12, 
                    background: '#f0f8ff', 
                    borderRadius: 4,
                    border: '1px solid #e0e0e0'
                  }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Space>
                        <Text strong style={{ fontSize: 16 }}>{pattern.label}</Text>
                        <Text type="secondary">({pattern.orientation})</Text>
                        <Text style={{ 
                          color: pattern.confidence > 80 ? '#52c41a' : '#faad14',
                          fontWeight: 'bold'
                        }}>
                          {pattern.confidence}% confident
                        </Text>
                      </Space>
                      <Text type="secondary">{pattern.characteristics}</Text>
                      {pattern.nearby_text && (
                        <Text type="secondary">Nearby text: "{pattern.nearby_text}"</Text>
                      )}
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        Location: ({Math.round(pattern.bounding_box.x)}, {Math.round(pattern.bounding_box.y)}) 
                        - Size: {Math.round(pattern.bounding_box.width)}x{Math.round(pattern.bounding_box.height)}
                      </Text>
                    </Space>
                  </div>
                ))}
              </Space>
            </Card>
          )}

          {/* Detected Measurements */}
          {results.joist_measurements && results.joist_measurements.length > 0 && (
            <Card title="Detected Measurements" style={{ marginBottom: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                {results.joist_measurements.map((measurement, index) => (
                  <div key={index} style={{ 
                    padding: 12, 
                    background: '#fff8f0', 
                    borderRadius: 4,
                    border: '1px solid #ffa940'
                  }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Space>
                        <Text strong style={{ fontSize: 18, color: '#fa541c' }}>
                          {measurement.pattern_label}
                        </Text>
                        <Text style={{ 
                          color: measurement.confidence > 0.8 ? '#52c41a' : '#faad14',
                          fontWeight: 'bold'
                        }}>
                          {(measurement.confidence * 100).toFixed(0)}% confident
                        </Text>
                      </Space>
                      
                      <Space direction="vertical">
                        <Text>
                          <strong>Horizontal Span:</strong> {measurement.horizontal_span_m.toFixed(3)}m
                        </Text>
                        {measurement.vertical_span_m && (
                          <Text>
                            <strong>Vertical Span:</strong> {measurement.vertical_span_m.toFixed(3)}m
                          </Text>
                        )}
                        <Text type="secondary">
                          Joist Count: {measurement.joist_count} | Method: {measurement.measurement_method}
                        </Text>
                      </Space>

                      {measurement.line_details && (
                        <div style={{ marginTop: 8, padding: 8, background: '#fafafa', borderRadius: 4 }}>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            Line Details: {JSON.stringify(measurement.line_details, null, 2)}
                          </Text>
                        </div>
                      )}
                    </Space>
                  </div>
                ))}
              </Space>
            </Card>
          )}

          {/* PDF with Measurement Visualization */}
          {results.joist_measurements && results.joist_measurements.length > 0 && fileList.length > 0 && (
            <PDFWithMeasurements
              file={fileList[0] as any as File}
              measurements={results.joist_measurements}
            />
          )}
        </>
      )}
    </div>
  );
};

export default ScaleDetectionDemo;