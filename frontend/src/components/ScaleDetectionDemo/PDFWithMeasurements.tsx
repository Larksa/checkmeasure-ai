import React, { useEffect, useState, useRef } from 'react';
import { Card, Spin } from 'antd';
import * as pdfjsLib from 'pdfjs-dist';
import MeasurementOverlay from '../pdf-viewer/MeasurementOverlay';

// Set up PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

interface PDFWithMeasurementsProps {
  file: File;
  measurements: any[];
}

const PDFWithMeasurements: React.FC<PDFWithMeasurementsProps> = ({ file, measurements }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loading, setLoading] = useState(true);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    renderPDF();
  }, [file]);

  const renderPDF = async () => {
    try {
      setLoading(true);
      
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
      
      // Get first page
      const page = await pdf.getPage(1);
      const viewport = page.getViewport({ scale: 1.5 });
      
      const canvas = canvasRef.current;
      if (!canvas) return;
      
      const context = canvas.getContext('2d');
      if (!context) return;
      
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      
      setDimensions({ width: viewport.width, height: viewport.height });
      
      await page.render({
        canvasContext: context,
        viewport: viewport,
      }).promise;
      
      setLoading(false);
    } catch (error) {
      console.error('Error rendering PDF:', error);
      setLoading(false);
    }
  };

  return (
    <Card title="PDF with Detected Measurements" style={{ marginBottom: 16 }}>
      <div style={{ position: 'relative', display: 'inline-block' }}>
        {loading && (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin size="large" tip="Rendering PDF..." />
          </div>
        )}
        
        <canvas
          ref={canvasRef}
          style={{
            display: loading ? 'none' : 'block',
            maxWidth: '100%',
            height: 'auto'
          }}
        />
        
        {!loading && measurements.length > 0 && (
          <MeasurementOverlay
            measurements={measurements}
            canvasWidth={dimensions.width}
            canvasHeight={dimensions.height}
            zoomLevel={1}
          />
        )}
      </div>
    </Card>
  );
};

export default PDFWithMeasurements;