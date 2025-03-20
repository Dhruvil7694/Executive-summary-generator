import React from 'react';
import ImageModal from './ImageModal';
import ImageThumbnail from './ImageThumbnail';

const ImageSection = ({ images, darkMode }) => {
  const [selectedImage, setSelectedImage] = React.useState(null);

  if (!images?.length) return null;

  return (
    <div className="mb-6">
      <h2
        className={`text-xl font-semibold mb-4 ${
          darkMode ? 'text-gray-300' : 'text-gray-700'
        }`}
      >
        Extracted Images ({images.length})
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {images.map((img, index) => {
          console.log(img); // Log to check what the image data is
          return (
            <ImageThumbnail
              key={`image-${index}`}
              image={img}
              darkMode={darkMode}
              onClick={() => setSelectedImage(img)}
            />
          );
        })}
      </div>
      {selectedImage && (
        <ImageModal
          image={selectedImage}
          darkMode={darkMode}
          onClose={() => setSelectedImage(null)}
        />
      )}
    </div>
  );
};

export default ImageSection;
