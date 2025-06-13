// src/components/MakeupTransferPage.jsx
import React, { useState } from "react";
import axios from "axios";

const MakeupTransferPage = () => {
  const [nonMakeup, setNonMakeup] = useState(null);
  const [makeup, setMakeup] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [alphas, setAlphas] = useState({
    eye: 1.0,
    eyebrow: 1.0,
    lip: 1.0,
    all: 1.0,
  });
  const [regions, setRegions] = useState(["all"]);
  const [loading, setLoading] = useState(false);

  const handleRegionToggle = (region) => {
    setRegions((prev) =>
      prev.includes(region)
        ? prev.filter((r) => r !== region)
        : [...prev, region]
    );
  };

  const handleSubmit = async () => {
    if (!nonMakeup || !makeup) return alert("두 이미지를 모두 업로드하세요.");

    const form = new FormData();
    form.append("non_makeup", nonMakeup);
    form.append("makeup", makeup);
    form.append("alpha_eye", alphas.eye);
    form.append("alpha_eyebrow", alphas.eyebrow);
    form.append("alpha_lip", alphas.lip);
    form.append("alpha_all", alphas.all);
    regions.forEach((r) => form.append("regions", r));

    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/makeup-transfer", form, {
        responseType: "blob",
      });
      const blobUrl = URL.createObjectURL(res.data);
      setResultUrl(blobUrl);
    } catch (err) {
      alert("메이크업 전이 실패");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 to-rose-200 flex justify-center items-center p-6">
      <div className="w-full max-w-5xl bg-white shadow-xl rounded-xl p-8">
        <h1 className="text-3xl font-bold text-center mb-6">💄 메이크업 전이 (CSD-MT)</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="flex flex-col items-center gap-2">
            <p className="font-semibold">Non-Makeup 이미지</p>
            <input type="file" accept="image/*" onChange={(e) => setNonMakeup(e.target.files[0])} />
          </div>
          <div className="flex flex-col items-center gap-2">
            <p className="font-semibold">Makeup 이미지</p>
            <input type="file" accept="image/*" onChange={(e) => setMakeup(e.target.files[0])} />
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {["eye", "eyebrow", "lip", "all"].map((region) => (
            <div key={region} className="text-center">
              <label className="block mb-1 text-sm font-medium">
                {region.toUpperCase()} Alpha
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={alphas[region]}
                onChange={(e) =>
                  setAlphas((prev) => ({ ...prev, [region]: parseFloat(e.target.value) }))
                }
              />
              <p className="text-xs text-gray-500">{alphas[region]}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-4 justify-center mb-6 flex-wrap">
          {["eye", "eyebrow", "lip", "all"].map((r) => (
            <button
              key={r}
              onClick={() => handleRegionToggle(r)}
              className={`px-4 py-2 rounded-full border ${
                regions.includes(r)
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              {r}
            </button>
          ))}
        </div>

        <div className="text-center">
          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`px-6 py-3 rounded-md font-semibold text-white shadow-md transition ${
              loading ? "bg-gray-400 cursor-not-allowed" : "bg-rose-500 hover:bg-rose-600"
            }`}
          >
            {loading ? "전이 중..." : "메이크업 전이 시작"}
          </button>
        </div>

        {resultUrl && (
          <div className="mt-10 text-center">
            <h2 className="text-xl font-semibold mb-2">🖼️ 전이 결과</h2>
            <img
              src={resultUrl}
              alt="메이크업 전이 결과"
              className="max-w-full mx-auto rounded-lg shadow"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default MakeupTransferPage;
