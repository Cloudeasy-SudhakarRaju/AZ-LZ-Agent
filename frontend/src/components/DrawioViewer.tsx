import React, { useEffect, useRef } from "react";

type DrawioViewerProps = {
  xmlData: string;
};

declare global {
  interface Window {
    GraphViewer: any;
  }
}

const DrawioViewer: React.FC<DrawioViewerProps> = ({ xmlData }) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!xmlData || !ref.current) return;

    // Clear previous content
    ref.current.innerHTML = '';

    try {
      // Parse the XML string to get the document element
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xmlData, "application/xml");
      
      // Check if GraphViewer is available (from viewer.min.js)
      if (typeof window.GraphViewer !== 'undefined') {
        // Create GraphViewer with container, xmlNode, and config
        new window.GraphViewer(ref.current, xmlDoc.documentElement, {});
      } else {
        // Fallback: show XML content in a readable format
        ref.current.innerHTML = `
          <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 15px; font-family: 'Courier New', monospace; white-space: pre-wrap; line-height: 1.4; max-height: 400px; overflow: auto;">
            <strong>Draw.io Diagram (XML Data):</strong><br><br>
            ${xmlData.replace(/</g, '&lt;').replace(/>/g, '&gt;')}
            <br><br>
            <em style="color: #6c757d;">Note: Draw.io viewer is not available. The diagram XML is shown above.</em>
          </div>
        `;
      }
    } catch (err) {
      console.error("Draw.io viewer error:", err);
      if (ref.current) {
        ref.current.innerHTML =
          `<p style="color: red;">❌ Failed to render Draw.io diagram: ${err}</p>`;
      }
    }
  }, [xmlData]);

  return (
    <div ref={ref} style={{ minHeight: "200px", width: "100%" }}>
      {!xmlData && <p style={{ color: "gray" }}>No diagram available</p>}
    </div>
  );
};

export default DrawioViewer;