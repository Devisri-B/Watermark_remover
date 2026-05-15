
# Image Watermark Remover
# Imports necessary libraries
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import cv2
import numpy as np
import os

try:
    from lama_cleaner.model_manager import ModelManager
    from lama_cleaner.default_config import Config
    LAMA_AVAILABLE = True
except ImportError:
    LAMA_AVAILABLE = False


class WatermarkRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Watermark Remover")
        self.root.geometry('1200x750')
        
        self.original_img = None
        self.current_filename = None
        self.mask = None
        self.drawing = False
        self.start_point = (0, 0)
        self.removal_method = "opencv"  # Default method
        self.lama_model = None
        
        # Setup GUI
        self.setup_gui()
    
    def setup_gui(self):
        # Top label
        title_label = tk.Label(
            self.root,
            text="Image Watermark Remover",
            font=("Arial", 50),
            fg="magenta"
        )
        title_label.place(x=80, y=10)
        
        # Instructions
        instr_label = tk.Label(
            self.root,
            text="Select an image with watermark, then draw rectangle around watermark area",
            font=("Arial", 14),
            fg="green"
        )
        instr_label.place(x=50, y=100)
        
        # Method selection frame
        method_frame = tk.LabelFrame(self.root, text="Removal Method", font=("Arial", 12), fg="blue")
        method_frame.place(x=50, y=150, width=400, height=120)
        
        # OpenCV method button
        opencv_btn = tk.Button(
            method_frame,
            text="Use OpenCV (Fast)",
            command=lambda: self.set_method("opencv"),
            font=("Arial", 12),
            bg="lightblue",
            fg="black"
        )
        opencv_btn.pack(pady=5)
        
        # Lama Cleaner method button
        if LAMA_AVAILABLE:
            lama_btn = tk.Button(
                method_frame,
                text="Use Lama Cleaner (AI - Best Quality)",
                command=lambda: self.set_method("lama"),
                font=("Arial", 12),
                bg="lightgreen",
                fg="black"
            )
            lama_btn.pack(pady=5)
        else:
            lama_status = tk.Label(
                method_frame,
                text="Lama Cleaner not installed\n(Install: pip install lama-cleaner torch torchvision)",
                font=("Arial", 10),
                fg="red"
            )
            lama_status.pack(pady=5)
        
        # Current method label
        self.method_label = tk.Label(
            self.root,
            text="Current method: OpenCV",
            font=("Arial", 12),
            fg="darkblue"
        )
        self.method_label.place(x=50, y=300)
        
        # Select button
        select_btn = tk.Button(
            self.root,
            text="SELECT IMAGE",
            command=self.select_image,
            font=("Arial", 20),
            bg="light green",
            fg="blue"
        )
        select_btn.place(x=80, y=600)
        
        # Clear button
        clear_btn = tk.Button(
            self.root,
            text="CLEAR MASK",
            command=self.clear_mask,
            font=("Arial", 20),
            bg="orange",
            fg="blue"
        )
        clear_btn.place(x=320, y=600)
        
        # Remove button
        remove_btn = tk.Button(
            self.root,
            text="REMOVE WATERMARK",
            command=self.remove_watermark,
            font=("Arial", 20),
            bg="yellow",
            fg="blue"
        )
        remove_btn.place(x=540, y=600)
        
        # Exit button
        exit_btn = tk.Button(
            self.root,
            text="EXIT",
            command=self.exit_app,
            font=("Arial", 20),
            bg="red",
            fg="blue"
        )
        exit_btn.place(x=950, y=600)
    
    def select_image(self):
        # Open file dialog
        filename = filedialog.askopenfilename(
            title="Select image file",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        self.current_filename = filename
        self.original_img = cv2.imread(filename)
        
        if self.original_img is None:
            messagebox.showerror("Error", "Could not load image")
            return
        
        # Initialize mask
        self.mask = np.zeros(self.original_img.shape[:2], dtype=np.uint8)
        
        # Show image and register mouse callback
        cv2.imshow("Image", self.original_img)
        cv2.setMouseCallback("Image", self.mouse_callback)
        messagebox.showinfo("Instructions", "Draw rectangle around watermark\nLeft click drag to select area\nPress any key when done")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def mouse_callback(self, event, x, y, flags, params):
        # Handle mouse events for drawing rectangle
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
        
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            img_copy = self.original_img.copy()
            cv2.rectangle(img_copy, self.start_point, (x, y), (0, 255, 0), 2)
            cv2.imshow("Image", img_copy)
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            # Create mask for the selected region
            cv2.rectangle(self.mask, self.start_point, (x, y), 255, -1)
            img_copy = self.original_img.copy()
            cv2.rectangle(img_copy, self.start_point, (x, y), (0, 255, 0), 2)
            cv2.imshow("Image", img_copy)
    
    def clear_mask(self):
        # Reset the mask
        if self.original_img is None:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        self.mask = np.zeros(self.original_img.shape[:2], dtype=np.uint8)
        messagebox.showinfo("Success", "Mask cleared. You can now draw a new selection.")
    
    def set_method(self, method):
        if method == "lama" and not LAMA_AVAILABLE:
            messagebox.showerror("Error", "Lama Cleaner is not installed\nPlease run: pip install lama-cleaner torch torchvision")
            return
        
        self.removal_method = method
        method_name = "Lama Cleaner (AI)" if method == "lama" else "OpenCV (Fast)"
        self.method_label.config(text=f"Current method: {method_name}")
        messagebox.showinfo("Success", f"Switched to {method_name}")
    
    def remove_watermark(self):
        if self.original_img is None:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        if self.mask is None or cv2.countNonZero(self.mask) == 0:
            messagebox.showwarning("Warning", "Please select watermark area first")
            return
        
        if self.removal_method == "lama":
            self.remove_watermark_lama()
        else:
            self.remove_watermark_opencv()
    
    def remove_watermark_opencv(self):
        try:
            # Show mask preview first
            mask_preview = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)
            cv2.imshow("Mask Preview (White = Area to Remove)", mask_preview)
            messagebox.showinfo("Mask Preview", "Check if the marked area is correct\nPress OK to continue with removal")
            cv2.destroyAllWindows()
            
            # Smooth the mask to avoid hard rectangular edges
            smooth_mask = self.mask.copy()
            
            # Dilate mask slightly to ensure full coverage
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            smooth_mask = cv2.dilate(smooth_mask, kernel, iterations=1)
            
            # Apply Gaussian blur to create soft edges
            smooth_mask = cv2.GaussianBlur(smooth_mask, (15, 15), 0)
            
            # Normalize to 0-255 range
            smooth_mask = np.uint8(smooth_mask)
            
            # Apply inpainting multiple times for better results
            result = self.original_img.copy()
            
            # First pass with smoothed mask
            result = cv2.inpaint(
                result,
                smooth_mask,
                5,
                cv2.INPAINT_NS
            )
            
            # Second pass for fine-tuning
            result = cv2.inpaint(
                result,
                cv2.GaussianBlur(smooth_mask, (5, 5), 0),
                3,
                cv2.INPAINT_TELEA
            )
            
            # Display result
            cv2.imshow("Original Image", self.original_img)
            cv2.imshow("Watermark Removed", result)
            messagebox.showinfo("Result", "Review the watermark removal result\nPress OK to save or close the image windows")
            
            # Ask to save
            if messagebox.askyesno("Save", "Save the result?"):
                output_path = filedialog.asksaveasfilename(
                    defaultextension=".jpg",
                    filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("All files", "*.*")]
                )
                if output_path:
                    cv2.imwrite(output_path, result)
                    messagebox.showinfo("Success", f"Image saved to {output_path}")
            
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove watermark: {str(e)}")
    
    def remove_watermark_lama(self):
        try:
            messagebox.showinfo("Loading", "Initializing Lama Cleaner AI model...\nThis may take a minute on first run")
            
            # Initialize Lama model on first use
            if self.lama_model is None:
                config = Config(device="cpu", use_cuda=False)
                self.lama_model = ModelManager(name="lama", device="cpu")
            
            # Show mask preview
            mask_preview = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)
            cv2.imshow("Mask Preview (White = Area to Remove)", mask_preview)
            messagebox.showinfo("Mask Preview", "Check if the marked area is correct\nPress OK to continue with removal")
            cv2.destroyAllWindows()
            
            # Prepare smooth mask for Lama
            smooth_mask = self.mask.copy()
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            smooth_mask = cv2.dilate(smooth_mask, kernel, iterations=1)
            smooth_mask = cv2.GaussianBlur(smooth_mask, (15, 15), 0)
            smooth_mask = np.uint8(smooth_mask)
            
            # Convert BGR to RGB for Lama
            img_rgb = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB)
            
            # Run Lama inpainting
            result_rgb = self.lama_model(img_rgb, smooth_mask)
            
            # Convert back to BGR
            result = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR)
            
            # Display result
            cv2.imshow("Original Image", self.original_img)
            cv2.imshow("Watermark Removed (Lama AI)", result)
            messagebox.showinfo("Result", "AI-powered watermark removal complete!\nPress OK to save or close the image windows")
            
            # Ask to save
            if messagebox.askyesno("Save", "Save the result?"):
                output_path = filedialog.asksaveasfilename(
                    defaultextension=".jpg",
                    filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("All files", "*.*")]
                )
                if output_path:
                    cv2.imwrite(output_path, result)
                    messagebox.showinfo("Success", f"Image saved to {output_path}")
            
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            messagebox.showerror("Error", f"Lama Cleaner failed: {str(e)}\nPlease ensure it's properly installed:\npip install lama-cleaner torch torchvision")
    
    def exit_app(self):
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            cv2.destroyAllWindows()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkRemoverApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()