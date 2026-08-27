function UploadBox({
  title,
  file,
  setFile,
  accept,
  optional = false,
}) {
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const removeFile = () => {
    setFile(null);
  };

  return (
    <div className="upload-area">

      {!file ? (

        <label className="upload-label">

          <div className="upload-icon">
            ↑
          </div>

          <strong>{title}</strong>

          <span>
            Click to select a file
          </span>

          <small>
            {optional
              ? "Optional • JPG, PNG"
              : "JPG, PNG or PDF"}
          </small>

          <input
            type="file"
            accept={accept}
            onChange={handleFileChange}
            hidden
          />

        </label>

      ) : (

        <div className="selected-file">

          <div className="file-icon">
            ✓
          </div>

          <div className="file-information">

            <strong>
              {file.name}
            </strong>

            <span>
              {(file.size / 1024).toFixed(1)} KB
            </span>

          </div>


          <button
            type="button"
            className="remove-file"
            onClick={removeFile}
          >
            ×
          </button>

        </div>

      )}

    </div>
  );
}

export default UploadBox;