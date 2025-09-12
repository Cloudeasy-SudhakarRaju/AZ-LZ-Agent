import React, { useEffect, useRef } from "react";
import mermaid from "mermaid";

type MermaidProps = {
  chart: string;
};

const Mermaid: React.FC<MermaidProps> = ({ chart }) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize mermaid with proper config
    mermaid.initialize({
      startOnLoad: false,
      theme: "default",
      securityLevel: "loose",
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true
      }
    });
  }, []);

  useEffect(() => {
    if (!chart || !ref.current) return;

    try {
      // Clear previous content
      ref.current.innerHTML = "";
      
      // Generate unique ID
      const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      // Create a temporary div for mermaid rendering
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = chart;
      
      // Use modern mermaid API
      mermaid.render(id, chart).then((result) => {
        if (ref.current) {
          ref.current.innerHTML = result.svg;
        }
      }).catch((error) => {
        console.error("Mermaid render error:", error);
        if (ref.current) {
          ref.current.innerHTML = `
            <div style="padding: 20px; text-align: center; color: #666;">
              <p>🔄 Diagram rendering in progress...</p>
              <p style="font-size: 0.9em; margin-top: 10px;">
                The Azure Landing Zone architecture diagram will appear here once rendered.
              </p>
            </div>
          `;
        }
      });
    } catch (err) {
      console.error("Mermaid setup error:", err);
      if (ref.current) {
        ref.current.innerHTML = `
          <div style="padding: 20px; text-align: center; color: #666;">
            <p>📊 Architecture Diagram Available</p>
            <p style="font-size: 0.9em; margin-top: 10px;">
              Please download the Draw.io file to view the detailed Azure architecture diagram.
            </p>
          </div>
        `;
      }
    }
  }, [chart]);

  return (
    <div 
      ref={ref} 
      style={{ 
        width: '100%', 
        minHeight: '200px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      {!chart && (
        <div style={{ color: "gray", textAlign: "center", padding: "20px" }}>
          No diagram available
        </div>
      )}
    </div>
  );
};

export default Mermaid;

