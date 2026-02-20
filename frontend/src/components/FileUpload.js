import React, { useRef } from 'react';
import './FileUpload.css';

function FileUpload({ onFileUpload, loading }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onFileUpload(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="file-upload">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        disabled={loading}
      />
      <button
        onClick={handleClick}
        className="upload-button"
        disabled={loading}
      >
        {loading ? 'Uploading...' : 'Choose Save File'}
      </button>
    </div>
  );
}

export default FileUpload;
