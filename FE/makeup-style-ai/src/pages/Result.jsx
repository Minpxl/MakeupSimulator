export default function Result() {
  return (
    <div className="p-6 max-w-2xl mx-auto bg-white rounded-lg shadow-md">
      <h2 className="text-3xl font-bold text-center mb-6 text-pink-600">메이크업 분석 결과</h2>
      <div className="mb-6 text-center">
        <p className="text-lg mb-2">💄 <span className="font-semibold text-pink-500">스타일 태그:</span> #글로시 #웜톤</p>
        <p className="text-gray-600">자연스러운 윤광과 MLBB 립으로 구성된 메이크업입니다.</p>
      </div>
      <h3 className="text-xl font-semibold mb-4 text-gray-800">추천 스타일</h3>
      <div className="flex justify-center gap-4">
        <img src="/sample1.jpg" alt="style1" className="w-24 h-24 object-cover rounded-lg shadow" />
        <img src="/sample2.jpg" alt="style2" className="w-24 h-24 object-cover rounded-lg shadow" />
        <img src="/sample3.jpg" alt="style3" className="w-24 h-24 object-cover rounded-lg shadow" />
      </div>
    </div>
  )
}
