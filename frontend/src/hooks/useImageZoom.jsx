import { useState, useRef } from 'react';

export const useImageZoom = () => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [translatePos, setTranslatePos] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  
  const dragStartRef = useRef({ x: 0, y: 0 });
  const currentTranslateRef = useRef({ x: 0, y: 0 });
  let animationFrameId = null;

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.1, 3));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.1, 1));
  const resetZoom = () => {
    setZoomLevel(1);
    setTranslatePos({ x: 0, y: 0 });
  };

  const startDragging = (e) => {
    setIsDragging(true);
    dragStartRef.current = {
      x: e.clientX - currentTranslateRef.current.x,
      y: e.clientY - currentTranslateRef.current.y,
    };
  };

  const stopDragging = () => {
    setIsDragging(false);
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  };

  const handleDragging = (e) => {
    if (!isDragging) return;

    const newTranslateX = e.clientX - dragStartRef.current.x;
    const newTranslateY = e.clientY - dragStartRef.current.y;

    currentTranslateRef.current = { x: newTranslateX, y: newTranslateY };

    if (!animationFrameId) {
      animationFrameId = requestAnimationFrame(() => {
        setTranslatePos({
          x: currentTranslateRef.current.x,
          y: currentTranslateRef.current.y,
        });
        animationFrameId = null;
      });
    }
  };

  return {
    zoomLevel,
    translatePos,
    isDragging,
    handleZoomIn,
    handleZoomOut,
    resetZoom,
    startDragging,
    stopDragging,
    handleDragging,
  };
};