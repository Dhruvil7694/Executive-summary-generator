import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useImageZoom } from '../../hooks/useImageZoom';
import { Maximize2, Minimize2, ZoomIn, ZoomOut, RotateCw, Download } from 'lucide-react';

// Custom Alert Component
const CustomAlert = ({ message, onClose }) => {
    useEffect(() => {
        const timer = setTimeout(onClose, 3000);
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg flex items-center">
            <span>{message}</span>
        </div>
    );
};

// Control Buttons Component
const ControlButtons = ({ 
    handleDownload, 
    handleRotate, 
    toggleFullScreen, 
    isFullScreen, 
    handleZoomIn, 
    handleZoomOut,
    zoomLevel,
    onClose,
    darkMode
}) => {
    const buttonClasses = `transition-all duration-200 rounded-md ${darkMode ? 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white' : 'bg-gray-800 text-white hover:bg-gray-700'}`;

    return (
        <>
            <div className="absolute top-4 right-4 flex items-center space-x-2 z-10">
                <button className={`${buttonClasses} p-2`} onClick={handleDownload} aria-label="Download image">
                    <Download size={20} />
                </button>
                <button className={`${buttonClasses} p-2`} onClick={handleRotate} aria-label="Rotate image">
                    <RotateCw size={20} />
                </button>
                <button className={`${buttonClasses} p-2`} onClick={toggleFullScreen} aria-label="Toggle fullscreen">
                    {isFullScreen ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
                </button>
                <button className={`${buttonClasses} px-3.5 py-2 rounded-full bg-red-500 text-white hover:bg-red-600`} onClick={onClose} aria-label="Close modal">
                    <span className="text-xl">×</span>
                </button>
            </div>
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center space-x-4 z-10">
                <button className={`${buttonClasses} p-2`} onClick={handleZoomOut} aria-label="Zoom out">
                    <ZoomOut size={20} />
                </button>
                <span className={`font-semibold px-3 py-2 rounded-lg transition-all duration-300`}>
                    {Math.round(zoomLevel * 100)}%
                </span>
                <button className={`${buttonClasses} p-2`} onClick={handleZoomIn} aria-label="Zoom in">
                    <ZoomIn size={20} />
                </button>
            </div>
        </>
    );
};

const ImageModal = ({ image, darkMode, onClose }) => {
    const { zoomLevel, translatePos, isDragging, handleZoomIn, handleZoomOut, resetZoom, startDragging, stopDragging, handleDragging } = useImageZoom();
    const [isFullScreen, setIsFullScreen] = useState(false);
    const [rotation, setRotation] = useState(0);
    const [errorMessage, setErrorMessage] = useState('');
    
    const modalRef = useRef(null);
    
    const modalClasses = `fixed inset-0 flex items-center justify-center z-50 bg-black ${isFullScreen ? 'bg-opacity-100' : 'bg-opacity-70'}`;
    
    const toggleFullScreen = async () => {
        try {
            if (!document.fullscreenElement) {
                await modalRef.current.requestFullscreen();
            } else {
                await document.exitFullscreen();
            }
            setIsFullScreen(!isFullScreen);
        } catch (error) {
            setErrorMessage('Fullscreen mode is not supported in your browser');
        }
    };

    const handleRotate = () => setRotation((prev) => (prev + 90) % 360);

    const handleDownload = async () => {
        try {
            const response = await fetch(image.base64_image);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `image-${image.page_number}.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            setErrorMessage('Failed to download image');
        }
    };

    // Keyboard event handlers
    const handleKeyPress = (e) => {
        switch (e.key) {
            case 'Escape':
                onClose();
                break;
            case '+':
                handleZoomIn();
                break;
            case '-':
                handleZoomOut();
                break;
            case '0':
                resetZoom();
                break;
            case 'r':
                handleRotate();
                break;
            case 'f':
                toggleFullScreen();
                break;
            default:
                break;
        }
    };

    useEffect(() => {
        document.addEventListener('keydown', handleKeyPress);
        return () => document.removeEventListener('keydown', handleKeyPress);
    }, []);

    return (
        <div className={modalClasses} role="dialog" aria-modal="true" ref={modalRef}>
            {errorMessage && <CustomAlert message={errorMessage} onClose={() => setErrorMessage('')} />}
            <ControlButtons 
                handleDownload={handleDownload}
                handleRotate={handleRotate}
                toggleFullScreen={toggleFullScreen}
                isFullScreen={isFullScreen}
                handleZoomIn={handleZoomIn}
                handleZoomOut={handleZoomOut}
                zoomLevel={zoomLevel}
                onClose={onClose}
                darkMode={darkMode}
            />
            <div className={`relative flex justify-center items-center h-full w-full overflow-hidden cursor-grab active:cursor-grabbing ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`} 
                 onMouseDown={startDragging} 
                 onMouseUp={stopDragging} 
                 onMouseMove={handleDragging}>
                 <img src={`data:image/png;base64,${image.base64_image}`} alt={`Page ${image.page_number}`} 
                      style={{ transform: `translate(${translatePos.x}px, ${translatePos.y}px) scale(${zoomLevel}) rotate(${rotation}deg)` }} />
             </div>
        </div>
    );
};

export default ImageModal;
