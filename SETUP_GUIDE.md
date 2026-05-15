SETUP INSTRUCTIONS

Python 3.12 Environment (Recommended for macOS):

1. Create conda environment with Python 3.12:
   conda create -n watermark_env python=3.12 -y

2. Activate the environment:
   conda activate watermark_env

3. Install packages using conda (for better compatibility):
   conda install -c conda-forge pillow opencv numpy pytorch torchvision -y

4. Install lama-cleaner using the conda environment's pip:
   /opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/pip install lama-cleaner

5. Run the application:
   python image_watermark_remover.py

QUICK START (using the provided script):
   bash run.sh

TROUBLESHOOTING:

If you get "imghdr" not found error:
- Make sure you're using Python 3.12, not 3.13+
- Check which Python: which python
- Should show: /opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/python

If imports fail:
- Make sure conda environment is activated: conda activate watermark_env
- Verify packages: pip list | grep -E "(Pillow|opencv|torch|lama)"

If lama-cleaner installation fails:
- Try: /opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/pip install --upgrade pip
- Then: /opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/pip install lama-cleaner
