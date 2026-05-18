# Watermark Removal - React Frontend

Production-grade React + TypeScript frontend for the watermark removal API.

## Features

- Drag-and-drop image upload
- Real-time watermark detection with visual feedback
- 5-method removal selector with availability status
- Before/after comparison with interactive slider
- Watermark mask visualization
- BRISQUE, SSIM, sharpness, and contrast quality metrics
- Dark mode support
- Responsive design
- Tailwind CSS styling

## Technologies

- React 18.2 + TypeScript 5.3
- Vite 5.0 (fast development & build)
- Tailwind CSS 3.3 (styling)
- Lucide React (icons)
- Axios (HTTP client)

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Development server runs on: **http://localhost:5173**

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts              # API client & types
│   │   └── index.ts               # Exports
│   │
│   ├── components/
│   │   ├── ImageUpload.tsx        # Drag-drop upload
│   │   ├── DetectionDisplay.tsx   # Detection results
│   │   ├── MethodSelector.tsx     # Method buttons
│   │   ├── BeforeAfterView.tsx    # Comparison slider
│   │   ├── QualityMetrics.tsx     # BRISQUE display
│   │   └── index.ts               # Exports
│   │
│   ├── App.tsx                    # Main application
│   ├── App.css                    # Tailwind styles
│   ├── main.tsx                   # Entry point
│   └── index.ts                   # Exports
│
├── public/
├── index.html                     # HTML template
├── package.json                   # Dependencies
├── tsconfig.json                  # TypeScript config
├── vite.config.ts                 # Vite config
├── tailwind.config.js             # Tailwind config
├── postcss.config.js              # PostCSS config
└── .eslintrc.json                 # ESLint config
```

## API Integration

The frontend connects to these backend endpoints:

### GET /health
Check server status and available methods.

### GET /api/methods
Get list of removal methods with details.

### POST /api/detect
Upload image for watermark detection.
- Returns: detection confidence, regions, method breakdown

### POST /api/remove
Remove watermark using selected method.
- Parameters: image file, mask file, method, quality_steps
- Returns: processed image, quality metrics

## Component Guide

### ImageUpload
- Drag-drop file upload
- File type validation (image/*)
- Loading state indicator

### DetectionDisplay
- Watermark detected status
- Confidence percentage with progress bar
- Individual detection method scores (FFT, edges, color, alpha)
- Detected regions list

### MethodSelector
- 5 removal method buttons
- Speed and quality badges
- Availability status
- Selected method highlight

### BeforeAfterView
- Side-by-side image comparison
- Draggable slider for manual comparison
- Watermark mask visualization
- Toggle between before/after and mask

### QualityMetrics
- BRISQUE score (before/after + improvement)
- SSIM (structural similarity)
- Sharpness comparison
- Contrast comparison
- Improvement summary

## Environment Variables

```bash
VITE_API_URL=http://localhost:8000/api  # Backend API URL
```

## Development Tips

### Hot Module Replacement
Vite enables instant updates on code changes - no full page reload needed.

### Tailwind IntelliSense
For better IDE support, install the "Tailwind CSS IntelliSense" VS Code extension.

### TypeScript Checking
```bash
# Check types without building
npx tsc --noEmit
```

### Linting
```bash
npm run lint
```

## Performance Optimization

- Lazy loading for image comparison
- Memoized components to prevent unnecessary re-renders
- Optimized image sizing
- CSS-only animations (no JS-based)
- Minimal bundle size with Vite

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### CORS errors
Ensure the Vite dev server is proxying to the backend correctly in `vite.config.ts`:
```js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

### Connection refused
Make sure the backend API is running on http://localhost:8000

### Image not displaying
Check console for CORS or network errors. Verify backend is returning proper image data.

## Deployment

To deploy to production:

1. Build the application:
   ```bash
   npm run build
   ```

2. Output is in the `dist/` directory

3. Serve with your web server:
   ```bash
   npx http-server dist/
   ```

4. Or deploy to a hosting service (Vercel, Netlify, etc.)

## Always check the correctness of AI-generated responses.
