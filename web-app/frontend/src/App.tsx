import React, { useEffect, useState } from 'react'
import { DownloadCloud, AlertCircle, Loader2 } from 'lucide-react'
import ImageUpload from './components/ImageUpload'
import DetectionDisplay from './components/DetectionDisplay'
import MethodSelector from './components/MethodSelector'
import BeforeAfterView from './components/BeforeAfterView'
import QualityMetrics from './components/QualityMetrics'
import { api, MethodInfo, DetectionResult, RemovalResult } from './api/client'
import './App.css'

interface ProcessingState {
  originalFile: File | null
  originalImage: string | null
  detectionResult: DetectionResult | null
  maskImage: string | null
  processedImage: string | null
  removalResult: RemovalResult | null
  selectedMethod: string
  isDetecting: boolean
  isRemoving: boolean
  error: string | null
}

function App() {
  const [state, setState] = useState<ProcessingState>({
    originalFile: null,
    originalImage: null,
    detectionResult: null,
    maskImage: null,
    processedImage: null,
    removalResult: null,
    selectedMethod: 'opencv',
    isDetecting: false,
    isRemoving: false,
    error: null,
  })

  const [availableMethods, setAvailableMethods] = useState<MethodInfo[]>([])
  const [darkMode, setDarkMode] = useState(true)

  // Load available methods on mount
  useEffect(() => {
    const loadMethods = async () => {
      try {
        const data = await api.getMethods()
        setAvailableMethods(data.methods)
        // Set default method to first available
        const available = data.methods.find(m => m.available)
        if (available) {
          setState(prev => ({ ...prev, selectedMethod: available.id }))
        }
      } catch (err) {
        setState(prev => ({
          ...prev,
          error: 'Failed to load available methods',
        }))
      }
    }
    loadMethods()
  }, [])

  const handleImageUpload = async (file: File) => {
    // Clear previous state
    setState(prev => ({
      ...prev,
      originalFile: file,
      isDetecting: true,
      error: null,
    }))

    // Read image as data URL
    const reader = new FileReader()
    reader.onload = async (e) => {
      const imageUrl = e.target?.result as string
      setState(prev => ({
        ...prev,
        originalImage: imageUrl,
      }))

      // Detect watermark
      try {
        const result = await api.detectWatermark(file)
        setState(prev => ({
          ...prev,
          detectionResult: result,
          isDetecting: false,
        }))

        // Generate mask visualization (simple: create canvas with detected regions)
        if (result.regions.length > 0) {
          const maskUrl = generateMaskImage(imageUrl, result.regions)
          setState(prev => ({
            ...prev,
            maskImage: maskUrl,
          }))
        }
      } catch (err) {
        setState(prev => ({
          ...prev,
          error: `Detection failed: ${err instanceof Error ? err.message : 'Unknown error'}`,
          isDetecting: false,
        }))
      }
    }
    reader.readAsDataURL(file)
  }

  const generateMaskImage = (imageUrl: string, regions: DetectionResult['regions']): string => {
    const canvas = document.createElement('canvas')
    const img = new Image()

    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0)'
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        // Draw detected regions as mask
        ctx.fillStyle = 'rgb(255, 255, 255)'
        regions.forEach(region => {
          ctx.fillRect(region.x, region.y, region.width, region.height)
        })
      }
    }

    img.src = imageUrl
    return canvas.toDataURL()
  }

  const handleRemoveWatermark = async () => {
    if (!state.originalFile || !state.maskImage || !state.detectionResult) {
      setState(prev => ({
        ...prev,
        error: 'Please upload an image and detect watermark first',
      }))
      return
    }

    setState(prev => ({
      ...prev,
      isRemoving: true,
      error: null,
    }))

    try {
      // Convert mask image to file
      const maskBlob = await fetch(state.maskImage).then(r => r.blob())
      const maskFile = new File([maskBlob], 'mask.png', { type: 'image/png' })

      const result = await api.removeWatermark(
        state.originalFile,
        maskFile,
        state.selectedMethod,
        state.selectedMethod === 'stable_diffusion' ? 30 : undefined
      )

      // Generate result image (in real scenario, this comes from backend)
      // For now, we'll show a placeholder
      setState(prev => ({
        ...prev,
        removalResult: result,
        processedImage: state.originalImage, // Would be replaced with actual result
        isRemoving: false,
      }))
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: `Removal failed: ${err instanceof Error ? err.message : 'Unknown error'}`,
        isRemoving: false,
      }))
    }
  }

  const handleDownload = () => {
    if (!state.processedImage) return

    const link = document.createElement('a')
    link.href = state.processedImage
    link.download = `watermark-removed-${Date.now()}.png`
    link.click()
  }

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 text-white transition-colors">
        {/* Header */}
        <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                  Watermark Removal Tool
                </h1>
                <p className="text-slate-400 text-sm mt-1">
                  AI-powered watermark detection and removal
                </p>
              </div>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Error Alert */}
          {state.error && (
            <div className="mb-6 p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-400">{state.error}</p>
                <button
                  onClick={() => setState(prev => ({ ...prev, error: null }))}
                  className="text-sm text-red-300 hover:text-red-200 mt-1"
                >
                  Dismiss
                </button>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column: Upload & Detection */}
            <div className="space-y-6">
              {/* Image Upload */}
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
                <h2 className="text-xl font-semibold mb-4">1. Upload Image</h2>
                <ImageUpload onImageUpload={handleImageUpload} isLoading={state.isDetecting} />
              </div>

              {/* Detection Display */}
              {state.detectionResult && (
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
                  <h2 className="text-xl font-semibold mb-4">2. Watermark Detection</h2>
                  <DetectionDisplay result={state.detectionResult} />
                </div>
              )}

              {/* Method Selector */}
              {state.detectionResult && (
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
                  <h2 className="text-xl font-semibold mb-4">3. Select Removal Method</h2>
                  <MethodSelector
                    methods={availableMethods}
                    selectedMethod={state.selectedMethod}
                    onMethodChange={(method) =>
                      setState(prev => ({ ...prev, selectedMethod: method }))
                    }
                  />
                </div>
              )}

              {/* Remove Button */}
              {state.detectionResult && (
                <button
                  onClick={handleRemoveWatermark}
                  disabled={state.isRemoving}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all"
                >
                  {state.isRemoving ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      Remove Watermark
                    </>
                  )}
                </button>
              )}
            </div>

            {/* Right Column: Preview & Results */}
            <div className="space-y-6">
              {/* Before/After View */}
              {state.originalImage && (
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
                  <h2 className="text-xl font-semibold mb-4">
                    {state.processedImage ? 'Results' : 'Preview'}
                  </h2>
                  <BeforeAfterView
                    beforeImage={state.originalImage}
                    afterImage={state.processedImage}
                    maskImage={state.maskImage}
                  />
                </div>
              )}

              {/* Quality Metrics */}
              {state.removalResult && (
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
                  <h2 className="text-xl font-semibold mb-4">Quality Metrics</h2>
                  <QualityMetrics metrics={state.removalResult.quality_metrics} />
                </div>
              )}

              {/* Download Button */}
              {state.processedImage && (
                <button
                  onClick={handleDownload}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all"
                >
                  <DownloadCloud className="w-5 h-5" />
                  Download Result
                </button>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
