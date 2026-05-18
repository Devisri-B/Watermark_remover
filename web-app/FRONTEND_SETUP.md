# Frontend Setup & Installation Guide

## Quick Start

### 1. Install Node.js

Download from https://nodejs.org (LTS version recommended)

Verify installation:
```bash
node --version
npm --version
```

### 2. Install Frontend Dependencies

```bash
cd /Users/devisri/Desktop/Research/Projects/Watermark/web-app/frontend
npm install
```

This installs:
- React 18.2 (UI framework)
- TypeScript 5.3 (type safety)
- Vite 5.0 (build tool)
- Tailwind CSS 3.3 (styling)
- Lucide React (icons)
- Axios (HTTP client)

Installation takes 2-5 minutes depending on internet speed.

### 3. Start Frontend Development Server

```bash
npm run dev
```

Frontend runs on: **http://localhost:5173**

Open your browser and navigate to this URL.

## Running Both Services

You need two terminals:

**Terminal 1 - Backend API:**
```bash
cd /Users/devisri/Desktop/Research/Projects/Watermark/web-app
/opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/python start_server.py
```
Runs on: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd /Users/devisri/Desktop/Research/Projects/Watermark/web-app/frontend
npm run dev
```
Runs on: http://localhost:5173

## Frontend Features

### Image Upload
- Click or drag-drop JPG, PNG, WebP images
- File validation (image type only)
- Size limit: 20MB (configurable)

### Watermark Detection
- Automatic detection on upload
- Shows confidence percentage (0-100%)
- Breaks down which detection methods found the watermark:
  - FFT (repeating patterns)
  - Edges (text/logos)
  - Color (colored marks)
  - Alpha (PNG overlays)
- Lists detected regions

### Method Selection
After detection, choose removal method:
1. **OpenCV Inpainting (Fast)** - ~500ms, medium quality
2. **Lama Cleaner (Best)** - ~1-3s, high quality
3. **Frequency Hybrid** - ~1s, medium-high quality
4. Other methods available if installed

### Before/After Comparison
- Drag slider to compare original and processed
- Toggle watermark mask visualization
- Shows percentage split

### Quality Metrics
After removal, view:
- **BRISQUE Score** - Image quality (lower is better)
- **SSIM** - Structural similarity
- **Sharpness** - Edge definition
- **Contrast** - Tone variation
- Improvement summary

### Download Result
Save processed image as PNG

## Development

### Project Structure
```
frontend/
├── src/
│   ├── api/client.ts           # Backend API integration
│   ├── components/             # React components
│   │   ├── ImageUpload.tsx
│   │   ├── DetectionDisplay.tsx
│   │   ├── MethodSelector.tsx
│   │   ├── BeforeAfterView.tsx
│   │   └── QualityMetrics.tsx
│   ├── App.tsx                 # Main component
│   └── main.tsx                # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### Component Hierarchy
```
App
├── ImageUpload (file upload)
├── DetectionDisplay (detection results)
├── MethodSelector (method choice)
├── BeforeAfterView (comparison)
└── QualityMetrics (results)
```

### Key Hooks & State Management

The App component uses React hooks:
- `useState` for local state (images, detection results)
- `useRef` for DOM references (slider, file input)
- `useEffect` for initialization (load methods on mount)

Main state object:
```typescript
{
  originalFile: File              // Uploaded file
  originalImage: string           // Base64 preview
  detectionResult: DetectionResult // Detection API response
  maskImage: string               // Mask visualization
  processedImage: string          // After processing
  removalResult: RemovalResult   // Removal API response
  selectedMethod: string          // Chosen removal method
  isDetecting: boolean            // Loading state
  isRemoving: boolean             // Processing state
  error: string | null            // Error message
}
```

## Build & Deployment

### Development Build
```bash
npm run dev
```
- Fast rebuild on file changes
- Full source maps for debugging
- Hot Module Replacement (HMR)

### Production Build
```bash
npm run build
```

Creates optimized bundle in `dist/` directory:
- Minified JavaScript & CSS
- Tree-shaking unused code
- Image optimization
- ~150KB gzipped

### Preview Production Build
```bash
npm run build
npm run preview
```

### Deploy to Production

Option 1: Serve locally
```bash
npx http-server dist/
```

Option 2: Deploy to Vercel (recommended)
```bash
npm i -g vercel
vercel
```

Option 3: Deploy to Netlify
```bash
npm i -g netlify-cli
netlify deploy --prod --dir dist
```

Option 4: Docker
Create a Dockerfile if needed for containerized deployment.

## Troubleshooting

### Issue: npm install fails
**Solution:** Clear npm cache and try again
```bash
npm cache clean --force
npm install
```

### Issue: "Cannot find module 'react'"
**Solution:** Ensure you're in the frontend directory
```bash
cd frontend
npm install
```

### Issue: "Connection refused" or "Cannot reach API"
**Solution:** Make sure backend is running on port 8000
```bash
curl http://localhost:8000/health
```

### Issue: CORS errors in console
**Solution:** Backend is configured for CORS, but ensure:
1. Backend is running
2. Frontend is on different port (5173)
3. Vite proxy is set up correctly in `vite.config.ts`

### Issue: Images not displaying
**Solution:** Check browser console for specific errors
1. Network tab - verify API response
2. Console tab - JavaScript errors
3. Application tab - check API response headers

### Issue: Slow image comparison slider
**Solution:** Use smaller images (< 5MB)
For now, the comparison is CSS-based (performant). No additional optimization needed.

## API Integration Details

### Detection Flow
1. User uploads image
2. Frontend reads file as base64 for preview
3. Frontend calls `POST /api/detect` with file
4. Backend returns detection results + confidence
5. Frontend generates mask visualization

### Removal Flow
1. User selects removal method
2. Frontend calls `POST /api/remove` with:
   - Original image file
   - Mask file (generated from detection)
   - Selected method ID
   - Quality steps (if applicable)
3. Backend processes and returns quality metrics
4. Frontend displays results

### Error Handling
All API calls wrapped in try-catch:
- Network errors → user-friendly message
- API errors → display error details
- Validation errors → highlight missing fields

## Performance Metrics

- First page load: ~2-3 seconds
- Detection: varies by image size (0.5-2s)
- Removal: varies by method (0.5s - 60s)
- File upload: depends on file size (< 1s for typical images)

## Environment Configuration

Create `.env.local` in frontend directory:
```bash
VITE_API_URL=http://localhost:8000/api
```

If deploying, update to point to production backend:
```bash
VITE_API_URL=https://api.example.com/api
```

## Code Style

- TypeScript for type safety
- React hooks (functional components)
- Tailwind for styling
- ESLint for code quality

To lint:
```bash
npm run lint
```

## Browser DevTools

Recommended Extensions:
- React Developer Tools (Chrome/Firefox)
- Redux DevTools (if needed in future)
- Tailwind CSS IntelliSense (VS Code)

## Security

- API key handling: None needed (local development)
- CORS: Configured on backend
- File uploads: Size limited to 20MB
- No sensitive data in frontend code

## Always check the correctness of AI-generated responses.
