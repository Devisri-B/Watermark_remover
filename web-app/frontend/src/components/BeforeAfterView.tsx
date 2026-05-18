import React, { useState, useRef, useEffect } from 'react'
import { Eye } from 'lucide-react'

interface BeforeAfterViewProps {
  beforeImage: string
  afterImage?: string
  maskImage?: string
}

function BeforeAfterView({ beforeImage, afterImage, maskImage }: BeforeAfterViewProps) {
  const [sliderPosition, setSliderPosition] = useState(50)
  const [showMask, setShowMask] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 })

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return

    const rect = containerRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percentage = (x / rect.width) * 100
    setSliderPosition(Math.max(0, Math.min(100, percentage)))
  }

  useEffect(() => {
    const img = new Image()
    img.onload = () => {
      setImageDimensions({ width: img.width, height: img.height })
    }
    img.src = beforeImage
  }, [beforeImage])

  const displayImage = showMask && maskImage ? maskImage : beforeImage

  return (
    <div className="space-y-3">
      {/* Image View */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        className="relative overflow-hidden rounded-lg bg-slate-900 border border-slate-700 cursor-col-resize group"
        style={{
          aspectRatio: imageDimensions.width / imageDimensions.height || '16/9',
        }}
      >
        {/* Before Image */}
        <div className="absolute inset-0">
          <img
            src={displayImage}
            alt="Before"
            className="w-full h-full object-contain"
          />
        </div>

        {/* After Image (visible portion) */}
        {afterImage && (
          <div
            className="absolute inset-y-0 left-0 overflow-hidden"
            style={{ width: `${sliderPosition}%` }}
          >
            <img
              src={afterImage}
              alt="After"
              className="w-full h-full object-contain"
              style={{ width: `${100 / (sliderPosition || 1) * 100}%` }}
            />
          </div>
        )}

        {/* Slider Handle */}
        {afterImage && (
          <div
            className="absolute top-0 bottom-0 w-1 bg-blue-400 group-hover:bg-blue-300 transition-colors"
            style={{ left: `${sliderPosition}%` }}
          >
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-blue-400 rounded-full p-2">
              <div className="flex items-center gap-1 text-xs font-semibold text-slate-900">
                <span>&lt;</span>
                <span>&gt;</span>
              </div>
            </div>
          </div>
        )}

        {/* Labels */}
        <div className="absolute top-4 left-4 px-2 py-1 bg-slate-900/75 rounded text-xs font-semibold text-slate-300">
          Before
        </div>
        {afterImage && (
          <div className="absolute top-4 right-4 px-2 py-1 bg-slate-900/75 rounded text-xs font-semibold text-slate-300">
            After
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3">
        {maskImage && (
          <button
            onClick={() => setShowMask(!showMask)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
              showMask
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
            }`}
          >
            <Eye className="w-4 h-4" />
            {showMask ? 'Hide Mask' : 'Show Mask'}
          </button>
        )}

        {afterImage && (
          <div className="flex-1 text-right text-xs text-slate-400">
            Drag slider to compare: {Math.round(sliderPosition)}% | {100 - Math.round(sliderPosition)}%
          </div>
        )}

        {!afterImage && (
          <div className="flex-1 text-sm text-slate-400">
            Processing result will appear here
          </div>
        )}
      </div>
    </div>
  )
}

export default BeforeAfterView
