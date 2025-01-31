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
        self.rect_id = None  # Initialize the rectangle ID for canvas
        
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

        # Canvas to draw rectangles
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=False)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
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
        """Display the currently loaded image with a max size constraint"""
        if self.processor.current_image is not None:
            image = Image.fromarray(self.processor.current_image)  # Convert OpenCV image to PIL Image
            
            # Define max width and height
            max_width, max_height = 800, 600  # Change this based on your requirement

            # Get original dimensions
            img_width, img_height = image.size

            # Scale image only if it's larger than max dimensions
            if img_width > max_width or img_height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)  # Resize while maintaining aspect ratio

            # Convert to PhotoImage
            self.photo_image = ImageTk.PhotoImage(image)

            # Update canvas size to match the image dimensions
            self.canvas.config(width=image.width, height=image.height)

            # Display image in canvas
            self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)

            # Adjust scroll region to fit the image
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))



    def on_mouse_press(self, event):
        """Store the initial position of mouse when clicked"""
        self.start_x, self.start_y = event.x, event.y

    def on_mouse_drag(self, event):
        """Draw a rectangle as the mouse is dragged"""
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.end_x, self.end_y = event.x, event.y
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.end_x, self.end_y, outline="blue", width=2
        )

    def on_mouse_release(self, event):
        """Handle the release of the mouse button (optional for now)"""
        # You can add any functionality here for the release event if needed
        pass
def main():
    root = tk.Tk()
    app = LoadingImage(root)  
    root.mainloop()


if __name__ == "__main__":
    main()