// src/components/FaceColorPage.jsx
import React, { useState } from "react";
import axios from "axios";

const FaceColorPage = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [manual, setManual] = useState({ x: "", y: "", hex: "", html: "", message: "", markedImage: null });
  const [sizeInfo, setSizeInfo] = useState("");

  const handleFileChange = (e) => {
    const img = e.target.files[0];
    setFile(img);
    setResult(null);
    setManual({ x: "", y: "", hex: "", html: "", message: "", markedImage: null });

    const reader = new FileReader();
    reader.onload = (ev) => {
      const img = new Image();
      img.onload = () => setSizeInfo(`이미지 크기: ${img.width}x${img.height}`);
      img.src = ev.target.result;
    };
    reader.readAsDataURL(img);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await axios.post("http://localhost:8000/enhance_and_analyze", form);
    setResult(res.data);
  };

  const handleManualSpoid = async () => {
    if (!file || !manual.x || !manual.y) return;
    const form = new FormData();
    form.append("file", file);
    form.append("x", manual.x);
    form.append("y", manual.y);
    const res = await axios.post("http://localhost:8000/manual_spoid", form);
    setManual((prev) => ({
      ...prev,
      hex: res.data.hex,
      html: res.data.html,
      message: res.data.message,
      markedImage: res.data.marked_image ? `data:image/png;base64,${res.data.marked_image}` : null
    }));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow">
      <h2 className="text-xl font-bold mb-4">💄 얼굴 색상 추출</h2>

      <input type="file" accept="image/*" onChange={handleFileChange} className="mb-4" />
      {sizeInfo && <p className="text-sm text-gray-500 mb-2">{sizeInfo}</p>}

      <div className="flex gap-4 mb-6">
        <button onClick={handleAnalyze} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">자동 추출</button>
        <button onClick={handleManualSpoid} className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">수동 추출</button>
      </div>

      {result && (
        <div className="grid grid-cols-3 gap-4">
          {["lip", "iris", "brow"].map((part) => (
            <div key={part} className="text-center">
              <p className="font-semibold mb-1">{part.toUpperCase()}</p>
              <div dangerouslySetInnerHTML={{ __html: result[`${part}_html`] }}></div>
              <p className="text-sm text-gray-700 mt-1">{result[`${part}_hex`]}</p>
            </div>
          ))}
        </div>
      )}

      <div className="mt-8">
        <h3 className="font-semibold text-lg mb-2">🧪 수동 추출</h3>
        <div className="flex gap-2 mb-4">
          <input type="text" placeholder="X 좌표" value={manual.x} onChange={(e) => setManual({ ...manual, x: e.target.value })} className="border px-2 py-1 rounded w-24" />
          <input type="text" placeholder="Y 좌표" value={manual.y} onChange={(e) => setManual({ ...manual, y: e.target.value })} className="border px-2 py-1 rounded w-24" />
        </div>
        {manual.message && <p className="text-sm text-gray-600">{manual.message}</p>}
        {manual.html && <div dangerouslySetInnerHTML={{ __html: manual.html }}></div>}
        {manual.hex && <p className="mt-1">HEX: {manual.hex}</p>}
        {manual.markedImage && (
          <div className="mt-4">
            <img src={manual.markedImage} alt="Marked" className="rounded border" />
          </div>
        )}
      </div>
    </div>
  );
};

export default FaceColorPage;
