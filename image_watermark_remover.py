
# Image Watermark Remover
# Advanced AI-powered watermark removal using Lama Cleaner
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import cv2
import numpy as np
import os

from lama_cleaner.model_manager import ModelManager
from lama_cleaner.default_config import Config


class WatermarkRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Watermark Remover - Powered by Lama Cleaner AI")
        self.root.geometry('1200x750')
        
        self.original_img = None
        self.current_filename = None
        self.mask = None
        self.drawing = False
        self.start_point = (0, 0)
        self.lama_model = None
        
        # Initialize Lama model
        try:
            messagebox.showinfo("Loading", "Initializing Lama Cleaner AI model...\nThis may take a moment on first run")
            self.config = Config(device="cpu", use_cuda=False)
            self.lama_model = ModelManager(name="lama", device="cpu")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Lama Cleaner: {str(e)}\n\nPlease ensure all dependencies are installed:\npip install -r requirements.txt")
            self.root.destroy()
            return
        
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
            text="Powered by Lama Cleaner AI - Draw rectangle around watermark area to remove",
            font=("Arial", 14),
            fg="green",
            bg="lightyellow"
        )
        instr_label.place(x=50, y=100)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Status: Ready. Using Lama Cleaner AI model",
            font=("Arial", 12),
            fg="darkblue"
        )
        self.status_label.place(x=50, y=160)
        
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
    
    def remove_watermark(self):
        if self.original_img is None:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        if self.mask is None or cv2.countNonZero(self.mask) == 0:
            messagebox.showwarning("Warning", "Please select watermark area first")
            return
        
        try:
            self.status_label.config(text="Status: Processing with Lama Cleaner AI...")
            self.root.update()
            
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
            
            self.status_label.config(text="Status: Processing complete!")
            
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
                    self.status_label.config(text="Status: Image saved successfully!")
            
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            self.status_label.config(text="Status: Ready. Using Lama Cleaner AI model")
            
        except Exception as e:
            self.status_label.config(text="Status: Error occurred")
            messagebox.showerror("Error", f"Watermark removal failed: {str(e)}")
    
    def exit_app(self):
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            cv2.destroyAllWindows()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkRemoverApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()