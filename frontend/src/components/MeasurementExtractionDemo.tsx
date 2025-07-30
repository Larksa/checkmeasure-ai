import React, { useState } from 'react';
import { Card, Button, Upload, message, Space, Spin, Typography, Input, Row, Col, List, Tag, Modal, Select } from 'antd';
import { UploadOutlined, FileSearchOutlined, EditOutlined, CheckOutlined, SelectOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import PDFViewer from './pdf-viewer/PDFViewer';
import { useAppStore } from '../stores/appStore';
import api from '../utils/api';

const { Title, Text } = Typography;
const { Option } = Select;

interface ScaleResult {
  scale_ratio: string;
  scale_notation?: string;  // Added for new scale system
  scale_factor: number;
  confidence: number;
  method: string;
  source_text?: string;
  calibration?: {
    method: string;
    status: string;
    pixels_per_mm: number;
    mm_per_pixel: number;
    confidence: number;
    reference_components: string[];
    details: any;
  };
}

interface MeasuredArea {
  id: string;
  label: string;
  detectedLabel?: string;
  selection: {
    x: number;
    y: number;
    width: number;
    height: number;
    pageNumber: number;
  };
  measurements?: {
    width_m: number;
    height_m: number;
    confidence: number;
  };
  calibrationMethod?: string;
  scaleUsed?: string;  // Added for new scale system
  status: 'pending' | 'analyzing' | 'success' | 'error';
  statusMessage?: string;
}

const MeasurementExtractionDemo: React.FC = () => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [scale, setScale] = useState<ScaleResult | null>(null);
  const [editingScale, setEditingScale] = useState(false);
  const [overrideScale, setOverrideScale] = useState('');
  const [measuredAreas, setMeasuredAreas] = useState<MeasuredArea[]>([]);
  const [editingLabel, setEditingLabel] = useState<string | null>(null);
  const [labelInput, setLabelInput] = useState('');
  const [manualScaleMode, setManualScaleMode] = useState(false);
  const [selectedPresetScale, setSelectedPresetScale] = useState<string>('1:100 at A3');
  
  const { 
    isSelecting, 
    setIsSelecting, 
    selectionAreas, 
    clearSelectionAreas 
  } = useAppStore();

  // Common architectural scales with paper size notation
  const commonScales = [
    { value: '1:20 at A3', label: '1:20 at A3 (Detail drawings)' },
    { value: '1:50 at A3', label: '1:50 at A3 (Floor plans - residential)' },
    { value: '1:100 at A3', label: '1:100 at A3 (Floor plans - commercial)' },
    { value: '1:200 at A3', label: '1:200 at A3 (Site plans)' },
    { value: '1:500 at A3', label: '1:500 at A3 (Large site plans)' },
    { value: '1:100 at A2', label: '1:100 at A2' },
    { value: '1:100 at A1', label: '1:100 at A1' },
    { value: '1:50 at A1', label: '1:50 at A1' },
    { value: 'custom', label: 'Custom...' }
  ];

  const handleScaleDetection = async () => {
    if (fileList.length === 0) {
      message.error('Please upload a PDF file first');
      return;
    }

    setAnalyzing(true);
    const file = fileList[0];

    try {
      const formData = new FormData();
      formData.append('file', file as any as File);
      
      const response = await api.post('/api/pdf/analyze-with-assumptions', formData, {
        headers: {
          'Content-Type': undefined
        }
      });

      setScale(response.data.scale);
      message.success(`Scale detected: ${response.data.scale.scale_ratio}`);
    } catch (error: any) {
      message.error(`Scale detection failed: ${error.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleManualScaleSet = () => {
    let scaleNotation = selectedPresetScale;
    
    if (selectedPresetScale === 'custom') {
      scaleNotation = overrideScale;
    }
    
    // Validate scale notation format
    const scalePattern = /1:(\d+)\s*(?:at|@)\s*([A-Za-z]\d)/;
    if (!scalePattern.test(scaleNotation)) {
      message.error('Please use format like "1:100 at A3"');
      return;
    }
    
    setScale({
      scale_ratio: scaleNotation,
      scale_notation: scaleNotation,
      scale_factor: 100, // No longer used but kept for compatibility
      confidence: 100,
      method: 'manual',
      source_text: 'User specified'
    });
    
    setManualScaleMode(false);
    message.success(`Scale set to ${scaleNotation}`);
  };

  const handleAreaSelection = () => {
    if (!scale) {
      message.warning('Please detect scale first');
      return;
    }
    setIsSelecting(true);
    message.info('Draw rectangles around areas to measure');
  };

  const handleAnalyzeArea = async (area: any) => {
    const measuredArea: MeasuredArea = {
      id: area.id,
      label: area.label || 'Area',
      selection: area,
      status: 'analyzing',
      statusMessage: 'Preparing area for analysis...'
    };
    
    setMeasuredAreas(prev => [...prev, measuredArea]);

    try {
      // Update status: uploading
      setMeasuredAreas(prev => prev.map(ma => 
        ma.id === area.id 
          ? { ...ma, statusMessage: 'Uploading PDF and area data...' }
          : ma
      ));

      const formData = new FormData();
      formData.append('file', fileList[0] as any as File);
      formData.append('request', JSON.stringify({
        selection_areas: [{
          x: area.x,
          y: area.y,
          width: area.width,
          height: area.height,
          page_number: area.pageNumber,
          calculation_type: 'joist'
        }],
        scale_notation: scale?.scale_notation || scale?.scale_ratio || '1:100 at A3'
      }));

      // Update status: analyzing with AI
      setMeasuredAreas(prev => prev.map(ma => 
        ma.id === area.id 
          ? { ...ma, statusMessage: 'Analyzing with Claude Vision AI... (this may take 30-60 seconds)' }
          : ma
      ));

      const response = await api.post('/api/pdf/analyze-selected-areas', formData, {
        headers: {
          'Content-Type': undefined
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            if (percentCompleted < 100) {
              setMeasuredAreas(prev => prev.map(ma => 
                ma.id === area.id 
                  ? { ...ma, statusMessage: `Uploading: ${percentCompleted}%` }
                  : ma
              ));
            }
          }
        }
      });

      // Extract detected label and measurements from response
      const result = response.data;
      console.log('Analysis response for area', area.id, ':', result);
      
      // Log measurements information
      if (result.measurements) {
        console.log('Measurement results:', {
          width_mm: result.measurements.width_mm,
          height_mm: result.measurements.height_mm,
          width_m: result.measurements.width_m,
          height_m: result.measurements.height_m,
          area_m2: result.measurements.area_m2,
          scale_used: result.measurements.scale_used
        });
      }
      
      // Log detected elements details
      if (result.detected_elements) {
        console.log(`Detected ${result.detected_elements.length} elements:`);
        result.detected_elements.forEach((elem: any, idx: number) => {
          console.log(`Element ${idx}:`, {
            label: elem.label,
            type: elem.type,
            measurements: elem.measurements,
            confidence: elem.confidence
          });
        });
      }
      
      const detectedElements = result.detected_elements || [];
      const measurements = result.measurements;
      
      // Use measurements from backend if available
      if (measurements) {
        message.success(`Measured using scale: ${measurements.scale_used}`);
      }
      
      if (detectedElements.length > 0) {
        const element = detectedElements[0];
        
        // Use measurements from backend calculation
        let width_m: number, height_m: number;
        if (measurements) {
          // Use backend-calculated measurements
          width_m = measurements.width_m;
          height_m = measurements.height_m;
        } else {
          // Fallback calculation (shouldn't happen with new system)
          width_m = area.width / 100; // Basic fallback
          height_m = area.height / 100;
        }
        
        // Update with detected label
        setMeasuredAreas(prev => prev.map(ma => 
          ma.id === area.id 
            ? {
                ...ma,
                detectedLabel: element.label,
                label: element.label, // Use detected label by default
                measurements: {
                  width_m: width_m,
                  height_m: height_m,
                  confidence: element.confidence || 0.8
                },
                scaleUsed: measurements?.scale_used || scale?.scale_notation,
                status: 'success'
              }
            : ma
        ));

        // Show modal to confirm/edit label
        setEditingLabel(area.id);
        setLabelInput(element.label || 'Area');
      } else {
        // No elements detected, but analysis completed
        setMeasuredAreas(prev => prev.map(ma => 
          ma.id === area.id 
            ? {
                ...ma,
                label: 'Unknown Area',
                measurements: {
                  width_m: area.width / (scale?.scale_factor || 100),
                  height_m: area.height / (scale?.scale_factor || 100),
                  confidence: 0.5
                },
                status: 'success',
                statusMessage: 'Analysis completed but no specific elements detected'
              }
            : ma
        ));
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
      setMeasuredAreas(prev => prev.map(ma => 
        ma.id === area.id 
          ? { ...ma, status: 'error', statusMessage: `Error: ${errorMessage}` } 
          : ma
      ));
      message.error(`Failed to analyze area: ${errorMessage}`);
      console.error('Area analysis error:', error);
    }
  };

  const handleLabelConfirm = () => {
    if (editingLabel) {
      setMeasuredAreas(prev => prev.map(ma => 
        ma.id === editingLabel ? { ...ma, label: labelInput } : ma
      ));
      setEditingLabel(null);
      setLabelInput('');
    }
  };

  const beforeUpload = (file: any) => {
    const isPDF = file.type === 'application/pdf';
    if (!isPDF) {
      message.error('You can only upload PDF files!');
      return false;
    }
    setFileList([file]);
    // Reset state when new file is uploaded
    setScale(null);
    setMeasuredAreas([]);
    clearSelectionAreas();
    return false;
  };

  // React to new selection areas
  React.useEffect(() => {
    const newAreas = selectionAreas.filter(
      area => !measuredAreas.find(ma => ma.selection.x === area.x && ma.selection.y === area.y)
    );
    
    newAreas.forEach(area => {
      handleAnalyzeArea(area);
    });
  }, [selectionAreas]);

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>
        <FileSearchOutlined /> Measurement Extraction
      </Title>
      
      <Row gutter={16}>
        <Col span={16}>
          {/* Upload and Controls */}
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

              <Space>
                <Button 
                  type="primary" 
                  onClick={handleScaleDetection}
                  loading={analyzing}
                  disabled={fileList.length === 0}
                >
                  Detect Scale
                </Button>

                <Button
                  onClick={() => setManualScaleMode(true)}
                  disabled={fileList.length === 0}
                >
                  Set Scale Manually
                </Button>

                <Button
                  onClick={handleAreaSelection}
                  disabled={!scale}
                  icon={<SelectOutlined />}
                >
                  Select Areas
                </Button>
              </Space>
            </Space>
          </Card>

          {/* Scale Display */}
          {scale && (
            <Card 
              title={
                <Space>
                  <span>Scale</span>
                  {scale.method === 'manual' && <Tag color="blue">Manual</Tag>}
                  {scale.method !== 'manual' && <Tag color="green">Detected</Tag>}
                </Space>
              } 
              style={{ marginBottom: 16 }}
            >
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
                    scale.scale_ratio
                  )}
                </Text>
                {editingScale ? (
                  <Button 
                    type="primary" 
                    icon={<CheckOutlined />} 
                    onClick={() => {
                      setEditingScale(false);
                      // Update scale if needed
                    }}
                  >
                    Save
                  </Button>
                ) : (
                  <Button 
                    icon={<EditOutlined />} 
                    onClick={() => {
                      setEditingScale(true);
                      setOverrideScale(scale.scale_ratio);
                    }}
                  >
                    Edit
                  </Button>
                )}
              </Space>
              <div style={{ marginTop: 8 }}>
                <Text type="secondary">
                  Method: {scale.method} | Confidence: {scale.confidence}%
                </Text>
              </div>
              
              {/* Scale Information */}
              {scale.scale_notation && (
                <div style={{ marginTop: 16, padding: 12, background: '#f0f8ff', borderRadius: 4 }}>
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Space>
                      <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      <Text strong>Scale Set</Text>
                    </Space>
                    <Text type="secondary">
                      Scale: {scale.scale_notation || scale.scale_ratio}
                    </Text>
                    <Text type="secondary">
                      Method: Mathematical calculation based on PDF dimensions
                    </Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      Measurements will be calculated using PDF coordinates and scale notation
                    </Text>
                  </Space>
                </div>
              )}
            </Card>
          )}

          {/* PDF Viewer */}
          {fileList.length > 0 && (
            <Card>
              <PDFViewer 
                file={fileList[0] as any as File}
                measurements={[]}
              />
            </Card>
          )}
        </Col>

        <Col span={8}>
          {/* Measured Areas Panel */}
          <Card title="Measured Areas" style={{ height: '100%' }}>
            <List
              dataSource={measuredAreas}
              renderItem={area => (
                <List.Item>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Space>
                      <Text strong>{area.label}</Text>
                      {area.status === 'analyzing' && <Spin size="small" />}
                      {area.status === 'success' && <Tag color="success">✓</Tag>}
                      {area.status === 'error' && <Tag color="error">✗</Tag>}
                    </Space>
                    
                    {/* Status message while analyzing */}
                    {area.status === 'analyzing' && area.statusMessage && (
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {area.statusMessage}
                      </Text>
                    )}
                    
                    {/* Error message */}
                    {area.status === 'error' && area.statusMessage && (
                      <Text type="danger" style={{ fontSize: '12px' }}>
                        {area.statusMessage}
                      </Text>
                    )}
                    
                    {/* Success results */}
                    {area.measurements && (
                      <>
                        <Text>
                          Dimensions: {area.measurements.width_m.toFixed(3)}m × {area.measurements.height_m.toFixed(3)}m
                        </Text>
                        <Text type="secondary">
                          Confidence: {(area.measurements.confidence * 100).toFixed(0)}%
                        </Text>
                        {area.calibrationMethod && (
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            Calibrated via: {area.calibrationMethod.replace('_', ' ')}
                          </Text>
                        )}
                      </>
                    )}
                    
                    {area.detectedLabel && area.detectedLabel !== area.label && (
                      <Text type="secondary">
                        Originally detected as: {area.detectedLabel}
                      </Text>
                    )}
                  </Space>
                </List.Item>
              )}
              locale={{ emptyText: 'No areas measured yet' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Label Edit Modal */}
      <Modal
        title="Confirm Area Label"
        open={!!editingLabel}
        onOk={handleLabelConfirm}
        onCancel={() => {
          setEditingLabel(null);
          setLabelInput('');
        }}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text>The AI detected this label. You can confirm or change it:</Text>
          <Input
            value={labelInput}
            onChange={(e) => setLabelInput(e.target.value)}
            placeholder="e.g., J1, G6, B2"
          />
        </Space>
      </Modal>

      {/* Manual Scale Selection Modal */}
      <Modal
        title="Set Scale Manually"
        open={manualScaleMode}
        onOk={handleManualScaleSet}
        onCancel={() => setManualScaleMode(false)}
        width={400}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text>Select a common architectural scale:</Text>
          <Select
            value={selectedPresetScale}
            onChange={setSelectedPresetScale}
            style={{ width: '100%' }}
          >
            {commonScales.map(scale => (
              <Option key={scale.value} value={scale.value}>
                {scale.label}
              </Option>
            ))}
          </Select>
          
          {selectedPresetScale === 'custom' && (
            <>
              <Text>Enter custom scale:</Text>
              <Input
                value={overrideScale}
                onChange={(e) => setOverrideScale(e.target.value)}
                placeholder="e.g., 1:75"
                style={{ marginTop: 8 }}
              />
            </>
          )}
        </Space>
      </Modal>
    </div>
  );
};

export default MeasurementExtractionDemo;