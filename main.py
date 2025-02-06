import os # used to save the cropped image
import tkinter as tk 
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk #PIL (Python Imaging Library) is used for image processing
import cv2 # OpenCV library for image processing
import numpy as np 

class ProcessImage:
    """
    This class handles the image loading and processing. 
    It provides functionality to load the chosen image using openCV and also handles colour conversion from BGR to RGB
    """
    def __ (self):
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
    """
    This class creates a complete GUI application with an image loading interface,
    cropping tools, and undo/redo capabilities. It uses tkinter for the GUI and
    provides a user-friendly interface for image manipulation.
    
    this class also has keyboard shortcuts: 
    Ctrl+Z: Undo last action
    Ctrl+Y: Redo last undone action
    Ctrl+S: Save cropped image
    Ctrl+O: Open/load image
    
    """
    def __init__(self, main_window):
        self.root = main_window # Setting the main GUI window
        self.root.title("Image Editor") # Sets the title 
        
        # Configure the window style
        self.root.configure(bg='#f0f0f0')  # Light gray background
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.configure('Primary.TButton', 
                           padding=10, 
                           font=('Helvetica', 10))
        self.style.configure('Secondary.TButton', 
                           padding=10, 
                           font=('Helvetica', 10))
        
        # Main container with padding
        self.main_container = ttk.Frame(self.root, padding="3")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Initialize variables
        self.processor = ProcessImage()
        self.start_x = self.start_y = self.end_x = self.end_y = None
        self.drawn_shapes = []
        self.undo_stack = []
        self.redo_stack = []
        self.active_handle = None
        self.handle_positions = {}
        self.original_coords = None
        self.create_toolbar()
        self.create_status_bar()
        self.create_canvas()
        self.keybind_shortcuts()
        self.root.bind("<Configure>", self.handle_resize)

    def create_resize_slider(self):
        """Creating a slider for resizing the preview of the cropped image"""
        self.slider_frame = ttk.LabelFrame(self.root, text="Resize Preview", padding="5")
        self.slider_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Slider widget (scale from 10% to 200%)
        self.resize_slider = ttk.Scale(self.slider_frame, from_=10, to=200, orient=tk.HORIZONTAL, command=self.resize_preview)
        self.resize_slider.set(100)  # Default size (100%)
        self.resize_slider.pack(fill=tk.X, padx=10, pady=5)

    def resize_preview(self, scale_value):
        """Resized the cropped image preview dynamically"""
        if self.cropped_image is None:
            return

        # Convert scale value to float and apply resizing
        scale_factor = float(scale_value) / 100.0
        image = Image.fromarray(self.cropped_image)

        # Compute new dimensions
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)

        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to Tkinter-compatible format and update display
        self.preview_image = ImageTk.PhotoImage(resized_image)
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, image=self.preview_image, anchor=tk.NW)

    def create_toolbar(self):
        """Creates a modern toolbar containing file and edit operation buttons"""
        # Create main toolbar container with padding
        self.toolbar = ttk.Frame(self.main_container)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # File operations section (Load/Save buttons)
        self.file_group = ttk.LabelFrame(self.toolbar, text="File", padding="5")
        self.file_group.pack(side=tk.LEFT, padx=5)
        
        # Load button - Allows selecting an image file
        self.load_button = ttk.Button(
            self.file_group,
            text="Load Image",
            style='Primary.TButton',
            command=self.load_image
        )
        self.load_button.pack(side=tk.LEFT, padx=2)
        
        # Save button - Initially disabled until image is cropped
        self.download_button = ttk.Button(
            self.file_group,
            text="Save Crop",
            style='Secondary.TButton',
            command=self.download_cropped_image,
            state=tk.DISABLED
        )
        self.download_button.pack(side=tk.LEFT, padx=2)
        
        # Edit operations section (Undo/Redo buttons)
        self.edit_group = ttk.LabelFrame(self.toolbar, text="Edit", padding="5")
        self.edit_group.pack(side=tk.LEFT, padx=5)
        
        # Undo button - Reverts last action
        self.undo_button = ttk.Button(
            self.edit_group,
            text="↶ Undo",
            style='Secondary.TButton',
            command=self.undo_state
        )
        self.undo_button.pack(side=tk.LEFT, padx=2)
        
        # Redo button - Reapplies previously undone action
        self.redo_button = ttk.Button(
            self.edit_group,
            text="↷ Redo",
            style='Secondary.TButton',
            command=self.redo_state
        )
        self.redo_button.pack(side=tk.LEFT, padx=2)
        
    def create_status_bar(self):
        """Creates a status bar at the bottom of the window to display app state and messages"""
        # Create label-based status bar with sunken effect and left-aligned text
        self.status_bar = ttk.Label(
            self.main_container,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_canvas(self):
        """Create the main canvas with a border and shadow effect"""
        # Container frame for the canvas with custom styling
        self.canvas_container = ttk.Frame(
            self.main_container,
            style='Canvas.TFrame'
        )
        self.canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Main canvas
        self.canvas = tk.Canvas(
            self.canvas_container,
            cursor="cross",  # Cross hair cursor for precise selection
            bg='white',
            highlightthickness=0,
            highlightbackground='#cccccc'  # Light gray border
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse event bindings for drawing/selection operations
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
    def keybind_shortcuts(self):
        """keybiind keyboard shortcuts"""
        self.root.bind('<Control-z>', lambda e: self.undo_action()) # Undo last action
        self.root.bind('<Control-y>', lambda e: self.redo_state())
        self.root.bind('<Control-s>', lambda e: self.download_cropped_image()) # Save image
        self.root.bind('<Control-o>', lambda e: self.load_image()) #load image
        
    """
    The methods in this section loads the image and display it in the tkinter GUI window 
    
    """
    def load_image(self):
        """Handles image file selection and loading the photo"""
        # load image using filedialog
        file_path = filedialog.askopenfilename(
             # Defines allowed file types
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*") 
            ]
        )

        # Process selected image if user didn't cancel
        if file_path:
            self.update_status(f"Loading image: {os.path.basename(file_path)}...") # Display the image name in the status bar
            # Attempt to load and display the image
            if self.processor.load_image(file_path):
                self.original_image = self.processor.get_current_image()
                self.display_image() # Display the loaded image
                self.update_status("Image loaded successfully")
            else:
                self.update_status("Failed to load image")

    def display_image(self):
        """Display the currently loaded image"""
        if self.processor.current_image is not None:
            image = Image.fromarray(self.processor.current_image)  # Convert OpenCV image to PIL Image 

            # get the current window size 
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Calculate scaling factor to fit window while maintaining the same asepct ratio 
            img_width, img_height = image.size
            width_ratio = canvas_width / img_width
            height_ratio = canvas_height / img_height
            scale_factor = min(width_ratio, height_ratio)
            
            # calculate the new dimesion 
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Store processed image for later use
            self.processed_image = np.array(image)  

            # Convert to Tkinter-compatible format
            self.photo_image = ImageTk.PhotoImage(image)
        
            # Center the image on canvas
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            
            # Clear previous content and display new image
            self.canvas.delete("all")
            self.canvas.create_image(x_offset, y_offset, image=self.photo_image, anchor=tk.NW)
    
    def handle_resize(self, event=None):
        """Handle window resize events by updating the image display"""
        if hasattr(self, 'processor') and self.processor.current_image is not None:
            # Add small delay to prevent rapid redraws during resizing
            if hasattr(self, "_resize_job"):
                self.root.after_cancel(self._resize_job)
            self._resize_job = self.root.after(100, self.display_image)
            
            
    def update_status(self, message):
        """Update status bar new message. message will be displayed on the bottom"""
        self.status_bar.config(text=message)

    """ 
    In this section the methods handle the cropping of image and applying the dark effect 
    
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
        
        try:
            image = self.processed_image.copy() # Create working copy of the image
            h, w, _ = image.shape

            # Create a dark overlay
            overlay = np.zeros((h, w, 3), dtype=np.uint8)
            overlay[:] = (0, 0, 0)  # Black overlay

            # Apply transparency to the overlay
            alpha = 0.6 # 60% transparency
            blended = cv2.addWeighted(image, 1 - alpha, overlay, alpha, 0) # Blend overlay with original image
 
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
            
        except Exception as e:
            self.update_status(f"Error applying mask: {str(e)}")

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
            self.canvas.delete(shape) # Delete the shape
        self.drawn_shapes.clear() # Clear the shapes

        if None not in (self.start_x, self.start_y, self.end_x, self.end_y): # Check if selection exists
            # Draw selection rectangle
            rect = self.canvas.create_rectangle( # Draw rectangle around the selected area
                self.start_x, self.start_y, 
                self.end_x, self.end_y, 
                outline="#2196F3", 
                width=2, 
                dash=(5, 2)  # Dashed line for better visibility
            )
            self.drawn_shapes.append(rect) # Append the rectangle to the shapes

            self.add_handles()
            
    def add_handles(self):
        handle_size = 6  # Size of the square handles

        # Compute center positions for each side
        mid_x = (self.start_x + self.end_x) // 2
        mid_y = (self.start_y + self.end_y) // 2

        # Define handle positions for each edge
        self.handle_positions = {
            "top": (mid_x, self.start_y),
            "bottom": (mid_x, self.end_y),
            "left": (self.start_x, mid_y),
            "right": (self.end_x, mid_y)
        }
        
        # Create handles with better visual style
        for position, (x, y) in self.handle_positions.items(): # Loop through each handle position
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill="#2196F3",  # Material Design Blue
                outline="white",
                width=1
            )
            self.drawn_shapes.append(handle)
            
            # # Draw handles (small squares)
            # top_handle = self.canvas.create_rectangle(mid_x - handle_size, self.start_y - handle_size,
            #                                           mid_x + handle_size, self.start_y + handle_size, fill="blue")  # Top-center
            # bottom_handle = self.canvas.create_rectangle(mid_x - handle_size, self.end_y - handle_size,
            #                                              mid_x + handle_size, self.end_y + handle_size, fill="blue")  # Bottom-center
            # left_handle = self.canvas.create_rectangle(self.start_x - handle_size, mid_y - handle_size,
            #                                            self.start_x + handle_size, mid_y + handle_size, fill="blue")  # Left-center
            # right_handle = self.canvas.create_rectangle(self.end_x - handle_size, mid_y - handle_size,
            #                                             self.end_x + handle_size, mid_y + handle_size, fill="blue")  # Right-center

            # Store handle IDs for deletion on next redraw
            # self.drawn_shapes.extend([top_handle, bottom_handle, left_handle, right_handle])


    def detect_handle(self, x, y): # This function checks if you clicked on a resize handle or not and if you click then it will atjust or
        handle_size = 6 # Size of the square handles
        # Check each handle's detection area
        for handle, (hx, hy) in self.handle_positions.items():
            if abs(x - hx) <= handle_size and abs(y - hy) <= handle_size: # Check if clicked on handle
                return handle # Return the handle name if clicked
        return None # Return None if not clicked on handle
    
        
    """
    
    This function resizes the rectangle when you drag a handle with top, bottom, left, or right handler
    and it also help to updates the rectangle's edges based on the mouse position while dragging the mouse in any 
    position of the image.
    
    """
    
    def adjust_rectangle(self, x, y):
        # Adjust the appropriate edge based on which handle is being dragged 
        if self.active_handle == "top":
            self.start_y = y # Move top edge vertically
        elif self.active_handle == "bottom":
            self.end_y = y # Move bottom edge vertically  
        elif self.active_handle == "left":
            self.start_x = x # Move left edge horizontally
        elif self.active_handle == "right":
            self.end_x = x  # Move right edge horizontally

    """ 
    *On Mouse Selection Handling*
    Basically, this function is responsible to select an area on the canvas using the mouse cursor.
    When you click the mouse it will take and update the x and y coordinates in their respective start_x and start_y coordinates and moving on with dragging it will add end_x and end_y.
    If a resize handle is detected and your resize the cropping image , it enables resizing instead of creating a new selection. 
    At the end when you release the mouse, it finalizes the selection area and make dark everything else outside the selected area.
    """
    def on_mouse_press(self, event): # This function is responsible for selecting the area on the canvas using the mouse cursor
        """Store the initial position of the mouse when clicked."""
        # Check if click is on a resize handle
        self.active_handle = self.detect_handle(event.x, event.y) # Detect handle if clicked
        
        if self.active_handle is None:
            # Start new selection if not clicking a handle
            self.start_x, self.start_y = event.x, event.y # Store initial coordinates
        else:
            # Store current coordinates for handle resizing
            self.original_coords = (self.start_x, self.start_y, self.end_x, self.end_y) # Store original coordinates

    def on_mouse_drag(self, event):
        """Draw a rectangle as the mouse is dragged, updating dynamically."""
        if self.active_handle: # Check if handle is active
            # Resize using handle
            self.adjust_rectangle(event.x, event.y) # Adjust rectangle based on handle
        else:
            # Update selection size
            self.end_x, self.end_y = event.x, event.y # Update end coordinates
        self.redraw_rectangle() # Redraw the rectangle

    def on_mouse_release(self, event):
        """Apply the selection mask when the mouse is released."""
        self.active_handle = None  # Reset active handle state
        if None not in (self.start_x, self.start_y, self.end_x, self.end_y): # Check if selection exists
            self.save_state()  # Save state before applying mask
            self.apply_selection_mask() # Apply the dark mask

    """
    This function download the cropped image in the same folder in which the program is running. 
    It first checks to see if the cropped image exists or not and then gets the current folder path using 
    os library and the image is saved as the name given "cropped_image.png"
    And at the end, a success message with the cropped image file path is displayed
    """
    def download_cropped_image(self):
        if self.cropped_image is not None: # Check if cropped image exists
            # current_directory = os.getcwd()
            # save_path = os.path.join(current_directory, "cropped_image.png")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
    
        if file_path:
            try:
                cropped_pil_image = Image.fromarray(self.cropped_image)
                cropped_pil_image.save(file_path)
                self.update_status(f"Image saved successfully to: {file_path}")
            except Exception as e:
                self.update_status(f"Error saving image: {str(e)}")
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            

    """
    Implements undo/redo functionality for image selections.

    This section maintains two stacks to track selection states:
    - undo_stack: Stores previous selection coordinates
    - redo_stack: Stores undone selections for potential redo

    Each state contains the coordinates (start_x, start_y, end_x, end_y) 
    of the selection rectangle. The system automatically updates button
    states based on stack availability.
    """
    
    def redo_state(self,event=None):
        """Redo the previously undone action"""
        if len(self.redo_stack) > 0:
            # Save current state to undo stack
            current_state = {
                'start_x': self.start_x, # Save current coordinates
                'start_y': self.start_y,
                'end_x': self.end_x,
                'end_y': self.end_y
            }
            self.undo_stack.append(current_state)
            
            # Restore state from redo stack
            next_state = self.redo_stack.pop()
            self.restore_state(next_state)
            
            # Update button states
            if len(self.redo_stack) == 0:
                self.redo_button.config(state=tk.DISABLED)
            self.undo_button.config(state=tk.NORMAL)
            
    def restore_state(self, state):
        """Helper method to restore a state and update the display"""
        if state:
            # Clear canvas first
            self.canvas.delete("all")
            
            # Restore coordinates that were saved
            self.start_x = state['start_x']
            self.start_y = state['start_y']
            self.end_x = state['end_x']
            self.end_y = state['end_y']
            
            # Redisplay the original image
            if self.processed_image is not None:
                print("Redisplaying original image")  # Debug print
                image = Image.fromarray(self.processed_image)
                self.photo_image = ImageTk.PhotoImage(image)
                self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)
            
            # Apply the mask and redraw the rectangle
            self.apply_selection_mask()
            self.redraw_rectangle()
            
            # Update status
            x1, x2 = sorted([self.start_x, self.end_x])
            y1, y2 = sorted([self.start_y, self.end_y])
            self.update_status(f"Selection area: {x2-x1}x{y2-y1} pixels")
            
    def save_state(self):
        """Save current selection state to undo stack"""
        if None not in (self.start_x, self.start_y, self.end_x, self.end_y):
            
            # Store current coordinates
            state = {
                'start_x': self.start_x,
                'start_y': self.start_y,
                'end_x': self.end_x,
                'end_y': self.end_y
            }
            
            self.undo_stack.append(state)
            self.redo_stack.clear() # Clear redo history on new action
            
            # Enable/disable undo/redo buttons based on curent stack state
            self.undo_button.config(state=tk.NORMAL)
            self.redo_button.config(state=tk.DISABLED)
            
    def undo_state(self, event=None):
        """Undo the last action and revers to the previous state"""
        if len(self.undo_stack) > 0:
            # Save current state to redo stack
            current_state = {
                'start_x': self.start_x,
                'start_y': self.start_y,
                'end_x': self.end_x,
                'end_y': self.end_y
            }
            self.redo_stack.append(current_state)
            
            # Restore previous state
            previous_state = self.undo_stack.pop()
            
            # Use the restore_state helper
            self.restore_state(previous_state)
            
            # Update button states
            if len(self.undo_stack) == 0:
                self.undo_button.config(state=tk.DISABLED)
            self.redo_button.config(state=tk.NORMAL)
            print(f"Undo stack after: {len(self.undo_stack)}")

    def get_current_image(self):
        return self.current_image
    
def main():
    
    root = tk.Tk() #create the main application window 
    root.geometry("1024x768")  # Set the window size, can be changed to other values (optional)
    app = LoadingImage(root) #starts the application with root window
    root.mainloop()    # Start the Tkinter event loop


if __name__ == "__main__":
    main()