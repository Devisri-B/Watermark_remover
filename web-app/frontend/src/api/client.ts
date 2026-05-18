import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api'

export interface DetectionResult {
  success: boolean
  confidence: number
  methods_used: number
  regions: Array<{
    x: number
    y: number
    width: number
    height: number
    area: number
  }>
  watermark_detected: boolean
  message: string
}

export interface RemovalResult {
  success: boolean
  method: string
  processing_time: number
  quality_metrics: {
    brisque_original: number
    brisque_processed: number
    ssim: number
    sharpness_original: number
    sharpness_processed: number
    contrast_original: number
    contrast_processed: number
    brisque_improvement: number
  }
  message: string
}

export interface MethodInfo {
  id: string
  name: string
  description: string
  available: boolean
  speed: string
  quality: string
}

class WatermarkAPI {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 600000, // 10 minutes for long operations
    })

    // Add error handling
    this.api.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error.response?.data?.detail || error.message)
        throw error
      }
    )
  }

  async getHealth() {
    const response = await this.api.get('/health')
    return response.data
  }

  async getMethods(): Promise<{ methods: MethodInfo[] }> {
    const response = await this.api.get('/methods')
    return response.data
  }

  async detectWatermark(file: File): Promise<DetectionResult> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await this.api.post<DetectionResult>('/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async removeWatermark(
    imageFile: File,
    maskFile: File,
    method: string,
    qualitySteps?: number
  ): Promise<RemovalResult> {
    const formData = new FormData()
    formData.append('file', imageFile)
    formData.append('mask_file', maskFile)
    formData.append('method', method)
    if (qualitySteps) {
      formData.append('quality_steps', qualitySteps.toString())
    }

    const response = await this.api.post<RemovalResult>('/remove', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }
}

export const api = new WatermarkAPI()
