import cv2
import pytesseract
import requests
from PIL import ImageGrab, Image
import numpy as np


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def split_string(s):
    if ';' in s:
        # Split the string by semicolons
        substrings = s.split(';')
        
        # Return the list of substrings
        return substrings
    else:
        return s


def imtext(image):

	# Convert the image to grayscale
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Optional: Apply some preprocessing
	# Thresholding (for binary image)
	_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

	# Noise removal (if needed)
	#thresh = cv2.medianBlur(thresh, 3)

	# Use pytesseract to extract text
	text = pytesseract.image_to_string(thresh)

	# return the extracted text
	return text

def ankisubmit(text, cloze, deck):

	# Define the URL for AnkiConnect
	anki_connect_url = "http://localhost:8765"

	# Define the payload for adding a cloze note
	payload = {
	    "action": "addNote",
	    "version": 6,
	    "params": {
	        "note": {
	            "deckName": f"{deck}",  # Change to your deck name
	            "modelName": "Cloze",  # Use the Cloze model
	            "fields": {
	                "Text": f"{cloze}",  # Cloze deletion syntax
	                "Back Extra": ""  # Optional additional info
	            },
	            "tags": ["geography"]  # Optional tags
	        }
	    }
	}

	# Send the request to AnkiConnect
	response = requests.post(anki_connect_url, json=payload)

	# Print the response
	print(response.json())

def replace_substring(main_string, substring):
    # Convert my_var to a string
    my_var_str = str(substring)
    
    # Create the replacement text with the variable
    replacement_text = f"{{{{c1::{my_var_str}}}}}"
    
    # Replace the substring with the replacement text
    result_string = main_string.replace(substring, replacement_text)
    
    return result_string

def replace_enters(s):
    return s.replace('\n', ' ').replace('\r', ' ')

def get_clip():
    try:
        # Grab the image from the clipboard
        img = ImageGrab.grabclipboard()
        
        if isinstance(img, Image.Image):
            # Convert the PIL image to a NumPy array
            img_np = np.array(img)
            
            # Convert RGB (PIL) to BGR (OpenCV)
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            return img_cv
        else:
            raise ValueError("No image in clipboard")
    except Exception as e:
        # Show an error message if something goes wrong
        messagebox.showerror("Error", f"Failed to paste image: {e}")
        return None
        

def main():

    deck = input("Target deck?: ")

    while True:
        text = input("Target cloze?: ")
        text = split_string(text)
        image = get_clip()

        cardtext = imtext(image)
        print(f"Detected text: {cardtext}")

        try:

            #cardtext = replace_enters(cardtext)
            if type(text) == str:
                cloze = replace_substring(cardtext, text)
                ankisubmit(cardtext, cloze, deck)

            elif type(text) == list:
                newtext = cardtext
                for item in text:
                    newtext = replace_substring(newtext, item)
                cloze = cardtext

                ankisubmit(cardtext, newtext, deck)

        except Exception as e:
            print(f"Could not add card, error: {str(e)}")



if __name__ == "__main__":
    main()