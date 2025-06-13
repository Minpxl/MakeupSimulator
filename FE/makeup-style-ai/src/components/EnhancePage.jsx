import React, { useState } from "react";
import axios from "axios";

const EnhancePage = () => {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [loading, setLoading] = useState(false);
  const [resultUrl, setResultUrl] = useState(null);
  const [originalUrl, setOriginalUrl] = useState(null);
  const [progress, setProgress] = useState(0);
  const [colorResult, setColorResult] = useState(null);
  const [nonMakeupFile, setNonMakeupFile] = useState(null);
  const [makeupFile, setMakeupFile] = useState(null);
  const [transferResult, setTransferResult] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setResultUrl(null);
    setOriginalUrl(URL.createObjectURL(file));
    setColorResult(null);
    setProgress(0);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const uploadRes = await axios.post("http://localhost:8000/upload", formData, {
        onUploadProgress: (e) => {
          const percent = Math.round((e.loaded * 100) / e.total);
          setProgress(percent);
        },
      });

      const uploadedFilename = uploadRes.data.filename;
      setFilename(uploadedFilename);

      await axios.post("http://localhost:8000/enhance");

      const resultFilename = uploadedFilename.replace(/\.(jpg|jpeg)$/i, ".png");
      setResultUrl(`http://localhost:8000/result/${resultFilename}`);
    } catch (err) {
      console.error("에러 발생:", err);
      alert("에러 발생: " + err.message);
    } finally {
      setLoading(false);
      setProgress(100);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/download?filename=${filename}`, {
        responseType: "blob",
      });

      const blob = new Blob([response.data], { type: response.headers["content-type"] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      const downloadFilename = filename.replace(/\.(jpg|jpeg)$/i, ".png");
      link.setAttribute("download", downloadFilename);

      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert("다운로드 실패");
      console.error(error);
    }
  };

  const handleAnalyze = async () => {
    try {
      const imgRes = await fetch(resultUrl);
      const imgBlob = await imgRes.blob();
      const restoredFile = new File([imgBlob], filename.replace(/\.(jpg|jpeg|png)$/i, ".png"), {
        type: "image/png",
      });

      const form = new FormData();
      form.append("file", restoredFile);

      const res = await axios.post("http://localhost:8000/analyze", form);
      setColorResult(res.data);
    } catch (err) {
      console.error("분석 실패:", err);
      alert("분석 실패: " + err.message);
    }
  };

  const handleReset = async () => {
    try {
      await axios.post("http://localhost:8000/reset");
      alert("초기화 완료!");
      setFile(null);
      setFilename("");
      setResultUrl(null);
      setOriginalUrl(null);
      setColorResult(null);
      setProgress(0);
    } catch (err) {
      alert("초기화 실패");
      console.error(err);
    }
  };

  const handleMakeupTransfer = async () => {
    if (!nonMakeupFile || !makeupFile) {
      alert("두 이미지를 모두 선택해주세요.");
      return;
    }

    const form = new FormData();
    form.append("non_makeup", nonMakeupFile);
    form.append("makeup", makeupFile);
    form.append("alpha_eye", 1.0);
    form.append("alpha_eyebrow", 1.0);
    form.append("alpha_lip", 1.0);
    form.append("alpha_all", 1.0);
    form.append("regions", "eye");
    form.append("regions", "eyebrow");
    form.append("regions", "lip");

    try {
      const res = await axios.post("http://localhost:8000/makeup-transfer", form, {
        responseType: "blob",
      });

      const blob = new Blob([res.data], { type: "image/png" });
      const url = URL.createObjectURL(blob);
      setTransferResult(url);
    } catch (err) {
      console.error("전이 실패:", err);
      alert("전이 실패: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-blue-100 flex items-center justify-center font-sans px-4 py-10">
      <div className="w-full max-w-5xl bg-white rounded-xl shadow-2xl p-8 animate-fade-in">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6 tracking-tight">✨ 얼굴 복원기 (CodeFormer)</h1>

        <div className="flex flex-col items-center gap-4">
          <label htmlFor="upload" className="cursor-pointer px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition duration-300">
            📁 파일 선택
          </label>
          <input id="upload" type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} className="hidden" />

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className={`w-full max-w-sm px-6 py-3 rounded-md font-semibold text-white shadow-md transform transition duration-300 ${
              loading ? "bg-gray-400 cursor-not-allowed" : "bg-emerald-500 hover:bg-emerald-600 hover:scale-105"
            }`}
          >
            {loading ? "복원 중..." : "🚀 복원 시작"}
          </button>

          <button
            onClick={handleReset}
            className="w-full max-w-sm px-6 py-3 rounded-md font-semibold text-white shadow-md bg-red-500 hover:bg-red-600 transition"
          >
            🧹 전체 초기화
          </button>
        </div>

        {loading && (
          <div className="w-full max-w-md mx-auto mt-6">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-center text-sm text-gray-500 mt-2">진행률: {progress}%</p>
          </div>
        )}

        {resultUrl && (
          <div className="mt-10">
            <h2 className="text-xl font-semibold text-center text-gray-700 mb-4">🖼️ 원본 vs 복원 비교</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="text-center">
                <p className="mb-2 text-sm text-gray-500">원본</p>
                <img src={originalUrl} alt="원본 이미지" className="w-full rounded-lg border border-gray-300 shadow-sm hover:shadow-lg transition" />
              </div>
              <div className="text-center">
                <p className="mb-2 text-sm text-gray-500">복원 결과</p>
                <img src={resultUrl} alt="복원 이미지" className="w-full rounded-lg border border-gray-300 shadow-sm hover:shadow-lg transition" />
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-center mt-8 gap-4">
          <button
            onClick={handleDownload}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md font-semibold shadow transition hover:scale-105"
          >
            🔽 복원 이미지 다운로드
          </button>
          <button
            onClick={handleAnalyze}
            disabled={!resultUrl}
            className={`px-6 py-3 rounded-md font-semibold text-white shadow transition hover:scale-105 ${
              resultUrl ? "bg-purple-600 hover:bg-purple-700" : "bg-gray-400 cursor-not-allowed"
            }`}
          >
            💄 분석 시작
          </button>
        </div>

        {colorResult && (
          <div className="mt-10">
            <h3 className="text-xl font-semibold mb-4 text-center text-gray-800">🎨 분석 결과</h3>
            <div className="grid grid-cols-3 gap-4">
              {["lip", "iris", "brow"].map((part) => (
                <div key={part} className="text-center">
                  <p className="text-sm font-semibold">{part.toUpperCase()}</p>
                  <div dangerouslySetInnerHTML={{ __html: colorResult[`${part}_html`] }}></div>
                  <p className="text-xs mt-1 text-gray-600">{colorResult[`${part}_hex`]}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-10 border-t pt-6">
          <h2 className="text-xl font-semibold mb-4 text-center text-gray-800">💄 메이크업 전이</h2>

          <div className="flex flex-col md:flex-row justify-center items-center gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">민낯 이미지</label>
              <input type="file" accept="image/*" onChange={(e) => setNonMakeupFile(e.target.files[0])} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">메이크업 이미지</label>
              <input type="file" accept="image/*" onChange={(e) => setMakeupFile(e.target.files[0])} />
            </div>
            <button
              onClick={handleMakeupTransfer}
              className="px-6 py-2 bg-pink-500 hover:bg-pink-600 text-white rounded-md font-semibold shadow"
            >
              💫 전이 시작
            </button>
          </div>

          {transferResult && (
            <div className="mt-6 text-center">
              <h3 className="text-md font-semibold mb-2">전이 결과</h3>
              <img src={transferResult} alt="전이 결과" className="mx-auto max-w-sm rounded shadow" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancePage;
