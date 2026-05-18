import React, { useRef, useState } from 'react'
import { Upload, Loader2 } from 'lucide-react'

interface ImageUploadProps {
  onImageUpload: (file: File) => void
  isLoading?: boolean
}

function ImageUpload({ onImageUpload, isLoading }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.type.startsWith('image/')) {
        onImageUpload(file)
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files
    if (files && files.length > 0) {
      onImageUpload(files[0])
    }
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
        isDragging
          ? 'border-blue-400 bg-blue-500/10'
          : 'border-slate-600 hover:border-slate-500 hover:bg-slate-700/30'
      } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        disabled={isLoading}
        className="hidden"
      />

      <div className="space-y-3">
        {isLoading ? (
          <>
            <Loader2 className="w-12 h-12 mx-auto text-blue-400 animate-spin" />
            <p className="text-slate-300">Detecting watermark...</p>
          </>
        ) : (
          <>
            <Upload className="w-12 h-12 mx-auto text-slate-400" />
            <div>
              <p className="text-lg font-semibold text-white">
                Drag and drop your image here
              </p>
              <p className="text-sm text-slate-400">
                or click to browse (JPG, PNG, WebP)
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default ImageUpload
