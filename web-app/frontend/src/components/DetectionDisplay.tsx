import React from 'react'
import { CheckCircle2, AlertCircle } from 'lucide-react'
import { DetectionResult } from '../api/client'

interface DetectionDisplayProps {
  result: DetectionResult
}

function DetectionDisplay({ result }: DetectionDisplayProps) {
  const confidencePercent = Math.round(result.confidence * 100)
  const confidenceColor =
    confidencePercent > 70 ? 'text-red-400' : confidencePercent > 40 ? 'text-yellow-400' : 'text-green-400'

  return (
    <div className="space-y-4">
      {/* Status */}
      <div className="flex items-center gap-3 p-4 rounded-lg bg-slate-700/50">
        {result.watermark_detected ? (
          <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0" />
        ) : (
          <CheckCircle2 className="w-6 h-6 text-green-400 flex-shrink-0" />
        )}
        <div>
          <p className="font-semibold">
            {result.watermark_detected ? 'Watermark Detected' : 'No Watermark Detected'}
          </p>
          <p className="text-sm text-slate-400">{result.message}</p>
        </div>
      </div>

      {/* Confidence Score */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <p className="font-medium">Confidence Score</p>
          <p className={`font-bold text-lg ${confidenceColor}`}>{confidencePercent}%</p>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              confidencePercent > 70
                ? 'bg-red-500'
                : confidencePercent > 40
                  ? 'bg-yellow-500'
                  : 'bg-green-500'
            }`}
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
      </div>

      {/* Method Breakdown */}
      {result.detection_methods_used > 0 && (
        <div className="space-y-2">
          <p className="font-medium text-sm text-slate-300">Detection Methods</p>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(result.individual_confidences).map(([method, score]) => (
              score > 0 && (
                <div key={method} className="p-2 rounded bg-slate-700/50">
                  <p className="text-xs text-slate-400 capitalize">{method}</p>
                  <p className="text-sm font-semibold text-blue-400">
                    {Math.round(score * 100)}%
                  </p>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Detected Regions */}
      {result.regions.length > 0 && (
        <div className="space-y-2">
          <p className="font-medium text-sm text-slate-300">
            Detected Regions ({result.regions.length})
          </p>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {result.regions.slice(0, 5).map((region, idx) => (
              <div key={idx} className="text-xs text-slate-400 p-2 bg-slate-700/50 rounded">
                <p>
                  Region {idx + 1}: {region.width}×{region.height}px at ({region.x}, {region.y})
                </p>
              </div>
            ))}
            {result.regions.length > 5 && (
              <p className="text-xs text-slate-500 p-2">
                +{result.regions.length - 5} more regions...
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default DetectionDisplay
