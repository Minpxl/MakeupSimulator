import { useState } from "react"
import { useNavigate } from "react-router-dom"

export default function Upload() {
  const [image, setImage] = useState(null)
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    setImage(URL.createObjectURL(e.target.files[0]))
  }

  const handleAnalyze = () => {
    navigate("/result")
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
      <div className="bg-white p-6 rounded-lg shadow max-w-lg w-full">
        <h2 className="text-2xl font-bold mb-4 text-center text-pink-600">이미지를 업로드해주세요</h2>
        <input type="file" accept="image/*" onChange={handleFileChange} className="mb-4 w-full text-sm" />
        {image && <img src={image} alt="preview" className="w-full h-auto object-cover mb-4 rounded" />}
        <button onClick={handleAnalyze} className="w-full bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600">
          분석하기
        </button>
      </div>
    </div>
  )
}
