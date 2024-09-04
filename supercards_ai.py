import cv2
import pytesseract
import requests
from PIL import ImageGrab, Image
import numpy as np
import openai


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
openai.api_key = 'PUT_YOUR_KEY_HERE'


def split_string(s):
    if ';' in s:
        # Split the string by semicolons
        substrings = s.split(';')
        
        # Return the list of substrings
        return substrings
    else:
        return s


def query_llm(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Ensure this is correct for your plan
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,  # Adjust the response length as needed
        n=1,
        stop=None,
        temperature=0.7,  # Adjust the creativity of the response
    )
    return response.choices[0].message['content'].strip()

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
        print(f"Failed to paste image: {e}")
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

                # Example usage
                prompt = f"Imagine you are a medical school professor who wants to write high quality flash cards in the program Anki to help students study. The flashcards use the cloze format which includes a set of curly braces around keywords, called the 'cloze'. A student has put together a string of text with at least one cloze in it but their grammar and formatting is poor. The student has promised you a great monetary reward in return for rewording the card. In addition, the student has occasionally left in out of place characters such as '*' or '¢', which should be replaced with a tab character when encountered. Please help the student reword the following cloze card while keeping the format of the 'cloze' word(s) exactly the same (along with the curly braces and colons). Also, presume all the words in the student's card to be relevant to the question they want to format. For example, a series of fragments may represent a list the student wants to learn. Please only respond with the exact text that should be in the reworded cloze card. Here is the student's card: {cloze}."
                result = query_llm(prompt)
                print(f"Card text: {result}")

                ankisubmit(cardtext, result, deck)

            elif type(text) == list:
                newtext = cardtext
                for item in text:
                    newtext = replace_substring(newtext, item)
                cloze = cardtext

                # Example usage
                prompt = f"Imagine you are a medical school professor who wants to write high quality flash cards in the program Anki to help students study. The flashcards use the cloze format which includes a set of curly braces around keywords, called the 'cloze'. A student has put together a string of text with at least one cloze in it but their grammar and formatting is poor. The student has promised you a great monetary reward in return for rewording the card. Please help the student reword the following cloze card while keeping the format of the 'cloze' word(s) exactly the same (along with the curly braces and colons). Also, presume all the words in the student's card to be relevant to the question they want to format. For example, a series of fragments may represent a list the student wants to learn. In addition, the student has occasionally left in out of place characters such as '*' or '¢', which should be replaced with a tab character when encountered. Please only respond with the exact text that should be in the reworded cloze card. Here is the student's card: {newtext}."
                result = query_llm(prompt)
                print(f"Card text: {result}")

                ankisubmit(cardtext, result, deck)

        except Exception as e:
            print(f"Could not add card, error: {str(e)}")



if __name__ == "__main__":
    main()