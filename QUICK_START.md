# Quick Start Guide - Image Watermark Remover

## Status: Ready to Use - Choose Your Method
The application is fully functional with TWO watermark removal methods to choose from!

## What You Get
- **OpenCV Inpainting**: Fast, lightweight, and reliable
- **Lama Cleaner AI**: Superior quality using deep learning (if available)

Pick the method that works best for your needs!

## Running the Application

### Option 1: Using the Run Script (Easiest)
```bash
cd /Users/devisri/Desktop/Research/Projects/Watermark
bash run.sh
```

### Option 2: Direct Command
```bash
conda activate watermark_env
python image_watermark_remover.py
```

### Option 3: Using Full Python Path
```bash
/opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/python /Users/devisri/Desktop/Research/Projects/Watermark/image_watermark_remover.py
```

## How to Use

1. **Click "SELECT IMAGE"** - Choose a watermarked image
2. **Select Detection Method** - Choose how to find the watermark:
   - Auto-Detect Watermark
   - Detect by Edges
   - Detect by Color Contrast
   - Manual Selection (Draw)
3. **Choose Removal Method** - Pick which algorithm to use:
   - **OpenCV Inpainting (Fast)** - Processes instantly, good results
   - **Lama Cleaner AI (Best Quality)** - Better results but takes longer
4. **Click "REMOVE WATERMARK"** - Process your image
5. **Save the Result** - Save your cleaned image

## Detection Methods Available

- **Auto-Detect**: Automatically finds watermarks using edge detection
- **Detect by Edges**: Uses edge detection algorithm
- **Detect by Color Contrast**: Finds watermarks by color differences
- **Manual Selection**: Draw a rectangle around the watermark

## Removal Methods

### OpenCV Inpainting (Fast & Reliable)
- Uses Navier-Stokes based inpainting
- Processes instantly
- Good for simple watermarks
- Lightweight, no AI model needed

### Lama Cleaner AI (Best Quality)
- Uses deep learning (ResNet-based)
- Superior quality results
- Best for complex watermarks
- Slower but more accurate
- Only available if installed

## Installation (If Starting Fresh)

```bash
# Create conda environment with Python 3.12
conda create -n watermark_env python=3.12

# Activate environment
conda activate watermark_env

# Install required packages
pip install -r requirements.txt
```

## Troubleshooting

### GUI doesn't appear
- Make sure you are in the watermark_env: `conda activate watermark_env`
- Try running from VS Code terminal

### Application crashes
- Verify conda environment is active: `which python`
- Check that all packages are installed: `pip list`
- See the full error: `python image_watermark_remover.py 2>&1`

### Lama Cleaner not available
- You can still use OpenCV method (just as effective for most watermarks)
- To install Lama Cleaner, run: `pip install lama-cleaner`

## Dependencies

- OpenCV (cv2) - Image processing and inpainting
- NumPy - Array operations
- PIL - Image display support
- Tkinter - GUI (usually pre-installed with Python)
- Lama Cleaner (optional) - AI inpainting for superior quality
- PyTorch (with Lama Cleaner) - Deep learning framework

All dependencies are in requirements.txt.

## Next Steps

1. Run the application
2. Select an image with a watermark
3. Auto-detect or manually select the watermark area
4. Choose your preferred removal method
5. Click "REMOVE WATERMARK"
6. Save the cleaned image

Enjoy removing watermarks!


