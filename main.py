import os 
import tkinter as tk 
from tkinter import filedialog
from PIL import Image, ImageTk #PIL (Python Imaging Library) is used for image processing
import cv2 # OpenCV library for image processing

class ProcessImage:
    def __init__(self):
        self.current_image = None #currently set as none but will store the loaded image
        self.current_image_path = None #stores the path of the chosen image 
        
    def load_image(self, image_path):
        """ Load an image using openCV """
        try: 
            image = cv2.imread(image_path) #reads the image using cv2
            if image is None:
                raise ValueError("Failed to load image") #checks if imgae loading failed or not 
            
            # Convert from BGR to RGB for display
            self.current_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #converst BGR to RGB using cv2
            self.current_image_path = image_path
            return True 
         
        except FileNotFoundError as e: # Handle case where file doesn't exist
            print(f"ERROR: {str(e)}")
            tk.messagebox.showerror("File Error", str(e))
            return False # Return False to indicate loading failed

            
        except Exception as e:  # Catch any other unexpected errors that might occur
            print(f"Unexpected error while loading image: {str(e)}")
            tk.messagebox.showerror("Error", f"Unexpected error while loading image: {str(e)}")
            return False
        
    def get_current_image(self):
        """Return the currently loaded image"""
        return self.current_image
    
    
class LoadingImage:
    def __init__(self, main_window):
        self.root = main_window #setting the main GUI window
        self.root.title("Image Viewer Application") # sets the title of the GUI
        
        self.processor = ProcessImage() #creates an instances of the first class
        
        # Create top frame for buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side='top', fill='x')  # Pack at top and fill horizontally
        # Create main frame for GUI elements
        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=150, pady=50) #padding arround the image 
        
        # Create buttons
        self.create_buttons()
        
        # Create image label
        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack(pady=10)
        
        # Store the PhotoImage reference
        self.photo_image = None
        
    def create_buttons(self):  
        """Create the button for loading the selected image"""
        
        button_frame = tk.Frame(self.root)  # Create frame in root instead of main_frame
        button_frame.pack(side="bottom", pady=10)  # Pack at top with some padding
        
        load_button = tk.Button(
            self.button_frame,
            text="Load Image",
            command=self.load_image
        )
        load_button.pack(pady=10) #adding padding above and below the button
        
    def load_image(self):
        """Open file dialog and load the selected image"""
        file_path = filedialog.askopenfilename(
             # Defines allowed file types
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*") 
            ]
        )
        
        if file_path:
            if self.processor.load_image(file_path):
                self.display_image()  # Display the loaded image
    
    def display_image(self): 
        """Display the currently loaded image"""
        if self.processor.current_image is not None:
            image = Image.fromarray(self.processor.current_image)  # Convert OpenCV image to PIL Image
            
            # Resize image if it's too large (optional)
            max_size = (800, 600)
            image.thumbnail(max_size, Image.Resampling.LANCZOS) # used for resmapling the image when its resized
            
            # Convert to PhotoImage
            self.photo_image = ImageTk.PhotoImage(image)
            
            # Update label with new image
            self.image_label.configure(image=self.photo_image)
            self.image_label.image = self.photo_image


def main():
    root = tk.Tk()
    app = LoadingImage(root)  
    root.mainloop()

