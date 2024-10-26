"use client";
import React, { useState } from "react";

const PaperUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
    }
  };

  return (
    <div className="card flex justify-center items-center p-4">
      <label className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded cursor-pointer w-48 h-16 flex items-center justify-center">
        Upload PDF
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="hidden"
        />
      </label>
      {file && <p className="mt-2">Selected file: {file.name}</p>}
    </div>
  );
};

export default PaperUpload;
