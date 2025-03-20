import React from 'react';

const ImageThumbnail = ({ image, darkMode, onClick }) => {
  return (
    <div className={`border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow ${
      darkMode 
        ? 'bg-gray-800 border-gray-700' 
        : 'bg-white border-gray-200'
    }`}>
      <div className="relative">
        <img
          src={`data:image/png;base64, ${image.base64_image}`}
          alt={`Extracted image from page ${image.page_number}`}
          className="w-full h-48 object-cover cursor-pointer rounded-md"
          onClick={onClick}
        />
        <span className={`absolute top-2 right-2 px-2 py-1 rounded-md text-sm ${
          darkMode 
            ? 'bg-gray-700 text-gray-300' 
            : 'bg-gray-800 text-white'
        }`}>
          Page {image.page_number}
        </span>
      </div>
    </div>
  );
};

export default ImageThumbnail;