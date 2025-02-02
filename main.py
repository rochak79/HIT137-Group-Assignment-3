import os # used to save the cropped image
import tkinter as tk 
from tkinter import filedialog
from PIL import Image, ImageTk #PIL (Python Imaging Library) is used for image processing
import cv2 # OpenCV library for image processing
import numpy as np

class ProcessImage:
    def __init__(self):
        self.current_image = None
        # self.current_image_path = None

    def load_image(self, image_path):
        """Load an image using OpenCV."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Failed to load image")

            # Convert from BGR to RGB
            self.current_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.current_image_path = image_path
            return True

        except Exception as e:
            print(f"Error: {str(e)}")
            tk.messagebox.showerror("Error", f"Unexpected error while loading image: {str(e)}")
            return False

    def get_current_image(self):
        """Return the currently loaded image."""
        return self.current_image


class LoadingImage:
    def __init__(self, main_window):
        self.root = main_window #setting the main GUI window
        self.root.title("Image Viewer Application") # sets the title of the GUI

        self.processor = ProcessImage() #creates an instances of the first class
        self.start_x = self.start_y = self.end_x = self.end_y = None
        self.drawn_shapes = []  # Store shape IDs to prevent multiple rectangles

        """
        These variables track and control the selection and resizing of a rectangle and they 
        store handle positions, detect interactions and also keep the original size for accurate resizing.
        """
        self.active_handle = None
        self.handle_positions = {}
        self.original_coords = None

         # Create top frame for buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side='top', fill='x')  # Pack at top and fill horizontally
        # Create main frame for GUI elements

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=150, pady=50) #padding arround the image 

        self.create_buttons()


        """ 
        *Drawing Canvas*
        The code here create a drawing canvas area inside the window using Tkinter after using this the whole window
        acts like a canvas where we user can draw any rectangles shapes using mouse to interact.

        
        When you click the left mouse button, a function runs and it is getting ready to draw.
        When you hold the button and move the mouse, another function runs and you can draw any shape.
        When you release the button, on_mouse_relase will run and stop at that point.
        """
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # Store the PhotoImage reference
        self.photo_image = None
        self.original_image = None  # Store original image
        # to store the croped image
        self.cropped_image = None

    def create_buttons(self):  
        """Create the button for loading the selected image"""
        
        # button_frame = tk.Frame(self.root)  # Create frame in root instead of main_frame
        # button_frame.pack(side="bottom", pady=10)  # Pack at top with some padding
        load_button = tk.Button(
            self.button_frame,
            text="Load Image",
            command=self.load_image
        )
        load_button.pack(pady=10) #adding padding above and below the button

        # this is the other button for downloading the image after being cropped and
        # this button is disabled at first and only active when user draw some rectangle shape in the image for cropping
        self.download_button = tk.Button(
            self.button_frame,
            text="Download Cropped Image",
            command=self.download_cropped_image,
            state=tk.DISABLED
        )
        self.download_button.pack(pady=10)

    def load_image(self):
        """Open file dialog and load the selected image"""
        file_path = filedialog.askopenfilename(
             # Defines allowed file types
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*") 
            ]
        )

        # 
        if file_path:
            if self.processor.load_image(file_path):
                self.original_image = self.processor.get_current_image()
                self.display_image() # Display the loaded image

    def display_image(self):
        """Display the currently loaded image"""
        if self.processor.current_image is not None:
            image = Image.fromarray(self.processor.current_image)  # Convert OpenCV image to PIL Image

            # Resize image if it's too large (optional)
            max_width, max_height = 800, 600
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS) # used for resmapling the image when its resized

            self.processed_image = np.array(image)  # Store for processing

            # Convert to PhotoImage
            self.photo_image = ImageTk.PhotoImage(image)

            """
            *Canvas Size*
            This code makes the canvas the same size as the image and then places the image 
            at the top-left corner which is (0,0) and it make sure it starts from the top-left corner 
            instead of another position.
            """
            self.canvas.config(width=image.width, height=image.height)
            self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)


    """ 
    *Applying Dark Effect outside the selected area*
    This function darkens everything outside the selected area while keeping the selected part normal. 
    It firstly check if an image is loaded or not and then it makes a copy of it to add a black overlay.
    The black overlay is slightly transparent and we choose it to make it 60%.
    After this the image looks darker and the selected ares is cleared by replacing it with the orginal image.
    Finally, the updated image is shown on the Tkinter canvas, and the selection box is redrawn.
    """
    def apply_selection_mask(self): 
        """Apply a dark mask to unselected areas and redraw the selection with handles."""
        if self.original_image is None or None in (self.start_x, self.start_y, self.end_x, self.end_y):
            return

        image = self.processed_image.copy()
        h, w, _ = image.shape

        # Create a dark overlay
        overlay = np.zeros((h, w, 3), dtype=np.uint8)
        overlay[:] = (0, 0, 0)  # Black overlay

        # Apply transparency to the overlay
        alpha = 0.6
        blended = cv2.addWeighted(image, 1 - alpha, overlay, alpha, 0)

        # Keep the selected region clear
        x1, x2 = sorted([self.start_x, self.end_x])
        y1, y2 = sorted([self.start_y, self.end_y])
        blended[y1:y2, x1:x2] = image[y1:y2, x1:x2]

        self.cropped_image = image[y1:y2, x1:x2]  # Save cropped image for download

        # Convert and display the masked image
        masked_image = Image.fromarray(blended)
        self.photo_image = ImageTk.PhotoImage(masked_image)
        self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)

        # Redraw the selection rectangle with handles
        self.redraw_rectangle()
        self.download_button.config(state=tk.NORMAL)  # Enable download button

    """
    *Selection Box Drawing in Rectangle*
    This function is helpful to darw a blue rectange around the selected area in all four rectangles sides
    which will be helpful to adjust the selection area from each side. Firslty, it removes an old shapes becuase it will creat a pattern of redrwing otherwise and checks if the selection area exists and olny draw the rectangle.
    It also calculate the center points of each side of the rectange and places four small handles to make resizing the cropping image easier.
    """
    def redraw_rectangle(self):
        """Redraw the rectangle with small square handles at the center of each side."""
        # Delete previously drawn rectangle & handles
        for shape in self.drawn_shapes:
            self.canvas.delete(shape)
        self.drawn_shapes.clear()

        if None not in (self.start_x, self.start_y, self.end_x, self.end_y):
            # Draw selection rectangle
            rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.end_x, self.end_y, outline="blue", width=2
            )
            self.drawn_shapes.append(rect)

            # Define handle size
            handle_size = 6

            # Compute center positions for each side
            mid_x = (self.start_x + self.end_x) // 2
            mid_y = (self.start_y + self.end_y) // 2

            """
            This code places small squares in the middle of each side of the rectangle so you can easily resize it.
            """
            self.handle_positions = {
                "top": (mid_x, self.start_y),
                "bottom": (mid_x, self.end_y),
                "left": (self.start_x, mid_y),
                "right": (self.end_x, mid_y)
            }

            # Draw handles (small squares)
            top_handle = self.canvas.create_rectangle(mid_x - handle_size, self.start_y - handle_size,
                                                      mid_x + handle_size, self.start_y + handle_size, fill="blue")  # Top-center
            bottom_handle = self.canvas.create_rectangle(mid_x - handle_size, self.end_y - handle_size,
                                                         mid_x + handle_size, self.end_y + handle_size, fill="blue")  # Bottom-center
            left_handle = self.canvas.create_rectangle(self.start_x - handle_size, mid_y - handle_size,
                                                       self.start_x + handle_size, mid_y + handle_size, fill="blue")  # Left-center
            right_handle = self.canvas.create_rectangle(self.end_x - handle_size, mid_y - handle_size,
                                                        self.end_x + handle_size, mid_y + handle_size, fill="blue")  # Right-center

            # Store handle IDs for deletion on next redraw
            self.drawn_shapes.extend([top_handle, bottom_handle, left_handle, right_handle])

    # This function checks if you clicked on a resize handle or not and if you click then it will atjust or
    # it will create a new handler and return None.
    def detect_handle(self, x, y):
        handle_size = 6
        for handle, (hx, hy) in self.handle_positions.items():
            if hx - handle_size <= x <= hx + handle_size and hy - handle_size <= y <= hy + handle_size:
                return handle
        return None
    
    """
    This function resizes the rectangle when you drag a handle with top, bottom, left, or right handler
    and it also help to updates the rectangle's edges based on the mouse position while dragging the mouse in any 
    position of the image.
    """
    def adjust_rectangle(self, x, y):
        start_x, start_y, end_x, end_y = self.original_coords

        if self.active_handle == "top":
            self.start_y = y
        elif self.active_handle == "bottom":
            self.end_y = y
        elif self.active_handle == "left":
            self.start_x = x
        elif self.active_handle == "right":
            self.end_x = x


    """ 
    *On Mouse Selection Handling*
    Basically, this function is responsible to select an area on the canvas using the mouse cursor.
    When you click the mouse it will take and update the x and y coordinates in their respective start_x and start_y coordinates and moving on with dragging it will add end_x and end_y.
    If a resize handle is detected and your resize the cropping image , it enables resizing instead of creating a new selection. 
    At the end when you release the mouse, it finalizes the selection area and make dark everything else outside the selected area.
    """
    def on_mouse_press(self, event):
        """Store the initial position of the mouse when clicked."""
        self.active_handle = self.detect_handle(event.x, event.y)
        if self.active_handle is None:
            self.start_x, self.start_y = event.x, event.y
        else:
            self.original_coords = (self.start_x, self.start_y, self.end_x, self.end_y)

    def on_mouse_drag(self, event):
        """Draw a rectangle as the mouse is dragged, updating dynamically."""
        if self.active_handle:
            self.adjust_rectangle(event.x, event.y)
        else:
            self.end_x, self.end_y = event.x, event.y
        self.redraw_rectangle()

    def on_mouse_release(self, event):
        """Apply the selection mask when the mouse is released."""
        self.active_handle = None
        self.apply_selection_mask()

    """
    This function download the cropped image in the same folder in which the program is running. 
    It first checks to see if the cropped image exists or not and then gets the current folder path using 
    os library and the image is saved as the name given "cropped_image.png"
    And at the end, a success message with the cropped image file path is displayed
    """
    def download_cropped_image(self):
        if self.cropped_image is not None:
            current_directory = os.getcwd()
            save_path = os.path.join(current_directory, "cropped_image.png")

            cropped_pil_image = Image.fromarray(self.cropped_image)
            cropped_pil_image.save(save_path)
            tk.messagebox.showinfo("Success", f"Image saved as {save_path}")


def main():
    root = tk.Tk()
    app = LoadingImage(root)
    root.mainloop()


if __name__ == "__main__":
    main()