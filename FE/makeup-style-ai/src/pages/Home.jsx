import { Link } from "react-router-dom"

export default function Home() {
  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-pink-100 to-yellow-100">
      <div className="bg-white shadow-lg rounded-xl p-8 text-center max-w-md">
        <h1 className="text-4xl font-bold mb-4 text-pink-600">Makeup Style AI</h1>
        <p className="text-gray-600 mb-6">AI가 당신의 메이크업 스타일을 분석해드립니다</p>
        <Link to="/upload" className="bg-pink-500 text-white px-6 py-2 rounded-full shadow hover:bg-pink-600">
          이미지 업로드하기
        </Link>
      </div>
    </div>
  )
}
