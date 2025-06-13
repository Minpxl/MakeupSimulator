"use client"

import { useState } from "react"
import axios from "axios"

const EnhancePage = () => {
  const [file, setFile] = useState(null)
  const [filename, setFilename] = useState("")
  const [loading, setLoading] = useState(false)
  const [resultUrl, setResultUrl] = useState(null)
  const [originalUrl, setOriginalUrl] = useState(null)
  const [progress, setProgress] = useState(0)
  const [colorResult, setColorResult] = useState(null)
  const [nonMakeupFile, setNonMakeupFile] = useState(null)
  const [makeupFile, setMakeupFile] = useState(null)
  const [transferResult, setTransferResult] = useState(null)

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setResultUrl(null)
    setOriginalUrl(URL.createObjectURL(file))
    setColorResult(null)
    setProgress(0)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const uploadRes = await axios.post("http://localhost:8000/upload", formData, {
        onUploadProgress: (e) => {
          const percent = Math.round((e.loaded * 100) / e.total)
          setProgress(percent)
        },
      })

      const uploadedFilename = uploadRes.data.filename
      setFilename(uploadedFilename)

      await axios.post("http://localhost:8000/enhance")

      const resultFilename = uploadedFilename.replace(/\.(jpg|jpeg)$/i, ".png")
      setResultUrl(`http://localhost:8000/result/${resultFilename}`)
    } catch (err) {
      console.error("에러 발생:", err)
      alert("에러 발생: " + err.message)
    } finally {
      setLoading(false)
      setProgress(100)
    }
  }

  const handleDownload = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/download?filename=${filename}`, {
        responseType: "blob",
      })

      const blob = new Blob([response.data], { type: response.headers["content-type"] })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url

      const downloadFilename = filename.replace(/\.(jpg|jpeg)$/i, ".png")
      link.setAttribute("download", downloadFilename)

      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert("다운로드 실패")
      console.error(error)
    }
  }

  const handleAnalyze = async () => {
    try {
      const imgRes = await fetch(resultUrl)
      const imgBlob = await imgRes.blob()
      const restoredFile = new File([imgBlob], filename.replace(/\.(jpg|jpeg|png)$/i, ".png"), {
        type: "image/png",
      })

      const form = new FormData()
      form.append("file", restoredFile)

      const res = await axios.post("http://localhost:8000/analyze", form)
      setColorResult(res.data)
    } catch (err) {
      console.error("분석 실패:", err)
      alert("분석 실패: " + err.message)
    }
  }

  const handleReset = async () => {
    try {
      await axios.post("http://localhost:8000/reset")
      alert("초기화 완료!")
      setFile(null)
      setFilename("")
      setResultUrl(null)
      setOriginalUrl(null)
      setColorResult(null)
      setProgress(0)
      setTransferResult(null)
      setNonMakeupFile(null)
      setMakeupFile(null)
    } catch (err) {
      alert("초기화 실패")
      console.error(err)
    }
  }

  const handleMakeupTransfer = async () => {

      window.open("http://127.0.0.1:7860", "_blank")

  }
  

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-100 px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* 헤더 섹션 */}
        <div className="text-center space-y-6 py-8">
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-pink-100 to-purple-100 rounded-full shadow-lg">
            <span className="text-2xl">✨</span>
            <span className="text-sm font-semibold text-gray-700 tracking-wide">AI 얼굴 복원 & 메이크업</span>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent leading-tight">
            얼굴 복원기
          </h1>
          <p className="text-gray-600 text-lg max-w-3xl mx-auto leading-relaxed">
            AI 기술로 흐릿한 얼굴 사진을 선명하게 복원하고, 색상 분석 및 메이크업 전이까지 한 번에 경험해보세요!
          </p>
        </div>

        {/* 메인 업로드 카드 */}
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">📸 이미지 업로드 & 복원</h2>
            <p className="text-gray-600">고품질 AI 복원을 위해 이미지를 업로드해주세요</p>
          </div>

          <div className="flex flex-col items-center gap-6">
            <label
              htmlFor="upload"
              className="group cursor-pointer flex flex-col items-center justify-center w-full max-w-lg h-40 border-3 border-dashed border-purple-300 rounded-2xl hover:border-purple-500 transition-all duration-300 bg-gradient-to-br from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 hover:scale-105"
            >
              <div className="text-6xl mb-3 group-hover:scale-110 transition-transform duration-300">📁</div>
              <span className="text-lg font-semibold text-gray-700 group-hover:text-gray-900 mb-1">
                {file ? file.name : "클릭하여 이미지 선택"}
              </span>
              <span className="text-sm text-gray-500">JPG, PNG 파일 지원 (최대 10MB)</span>
            </label>
            <input
              id="upload"
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files[0])}
              className="hidden"
            />

            <div className="flex flex-col sm:flex-row gap-4 w-full max-w-lg">
              <button
                onClick={handleUpload}
                disabled={!file || loading}
                className={`flex-1 px-8 py-4 rounded-2xl font-bold text-white shadow-xl transform transition-all duration-300 ${
                  loading
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 hover:scale-105 hover:shadow-2xl"
                }`}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    복원 중...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">🚀 복원 시작</span>
                )}
              </button>

              <button
                onClick={handleReset}
                className="px-8 py-4 rounded-2xl font-bold text-white shadow-xl bg-gradient-to-r from-red-400 to-red-500 hover:from-red-500 hover:to-red-600 transform transition-all duration-300 hover:scale-105 hover:shadow-2xl"
              >
                🧹 초기화
              </button>
            </div>
          </div>

          {/* 진행률 바 */}
          {loading && (
            <div className="w-full max-w-lg mx-auto mt-8 space-y-3">
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500 ease-out rounded-full"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-center text-lg font-semibold text-gray-700">진행률: {progress}%</p>
            </div>
          )}
        </div>

        {/* 결과 비교 섹션 */}
        {resultUrl && (
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8">
            <h2 className="text-2xl font-bold text-center text-gray-800 mb-8 flex items-center justify-center gap-3">
              👀 원본 vs 복원 비교
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div className="inline-block px-4 py-2 bg-gray-100 rounded-full text-sm font-semibold text-gray-700">
                  원본 이미지
                </div>
                <div className="relative group overflow-hidden rounded-2xl shadow-lg">
                  <img
                    src={originalUrl || "/placeholder.svg"}
                    alt="원본 이미지"
                    className="w-full aspect-square object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="inline-block px-4 py-2 bg-gradient-to-r from-emerald-100 to-teal-100 rounded-full text-sm font-semibold text-emerald-700">
                  복원된 이미지
                </div>
                <div className="relative group overflow-hidden rounded-2xl shadow-lg">
                  <img
                    src={resultUrl || "/placeholder.svg"}
                    alt="복원 이미지"
                    className="w-full aspect-square object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row justify-center gap-4 mt-8">
              <button
                onClick={handleDownload}
                className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white rounded-2xl font-bold shadow-xl transform transition-all duration-300 hover:scale-105 hover:shadow-2xl"
              >
                💾 이미지 다운로드
              </button>
              <button
                onClick={handleAnalyze}
                disabled={!resultUrl}
                className={`px-8 py-4 rounded-2xl font-bold shadow-xl transform transition-all duration-300 hover:scale-105 hover:shadow-2xl ${
                  resultUrl
                    ? "bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white"
                    : "bg-gray-300 text-gray-500 cursor-not-allowed"
                }`}
              >
                🎨 색상 분석
              </button>
            </div>
          </div>
        )}

        {/* 색상 분석 결과 */}
        {colorResult && (
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8">
            <h3 className="text-2xl font-bold mb-8 text-center text-gray-800 flex items-center justify-center gap-3">
              🌈 색상 분석 결과
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { key: "lip", label: "입술", emoji: "💋", gradient: "from-rose-400 to-pink-500" },
                { key: "iris", label: "홍채", emoji: "👁️", gradient: "from-blue-400 to-indigo-500" },
                { key: "brow", label: "눈썹", emoji: "🤨", gradient: "from-amber-400 to-orange-500" },
              ].map(({ key, label, emoji, gradient }) => (
                <div
                  key={key}
                  className="text-center space-y-4 p-6 bg-gradient-to-br from-gray-50 to-white rounded-2xl shadow-lg"
                >
                  <div
                    className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${gradient} text-white font-bold shadow-lg`}
                  >
                    <span className="text-lg">{emoji}</span>
                    {label}
                  </div>
                  <div
                    dangerouslySetInnerHTML={{ __html: colorResult[`${key}_html`] }}
                    className="flex justify-center"
                  />
                  <div className="inline-block px-3 py-1 bg-gray-100 rounded-full text-xs font-mono text-gray-600">
                    {colorResult[`${key}_hex`]}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 메이크업 전이 섹션 */}
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8">
          <h2 className="text-2xl font-bold mb-8 text-center text-gray-800 flex items-center justify-center gap-3">
            💄 메이크업 전이
          </h2>
          <div className="flex justify-center mb-8">
            <button
              onClick={handleMakeupTransfer}
              className={`px-10 py-4 rounded-2xl font-bold shadow-xl transform transition-all duration-300 hover:scale-105 hover:shadow-2xl ${
                   "bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white"

              }`}
            >
              ✨ 메이크업 전이 시작
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EnhancePage
