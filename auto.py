import webbrowser
import pyautogui
import time
import os
import pyperclip
import google.generativeai as genai
from tkinter import Tk, Label, Button, Frame, StringVar, simpledialog

class GiphyUploader:
    def __init__(self):
        self.root = Tk()
        self.root.title("GIPHY Upload Automation")
        self.root.geometry("500x450")
        self.root.configure(bg='#121212')
        
        # Status variable
        self.status = StringVar()
        self.status.set("Ready to start GIPHY upload process")
        
        # Store the user name for later use
        self.user_name = ""
        
        # Configure Gemini AI
        self.setup_gemini()
        
        # Create UI
        self.create_ui()
        
        # Set up pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
    def setup_gemini(self):
        """Configure the Gemini AI for tag generation"""
        try:
            genai.configure(api_key="your api key ")
            
            # List available models properly
            def get_available_models():
                try:
                    models = list(genai.list_models())
                    names = [m.name for m in models]
                    print("Available models:", names)
                    return names
                except Exception as e:
                    print("❌ Could not list models:", e)
                    return []

            # Pick a working model
            available = get_available_models()
            preferred = ["gemini-2.0-flash-exp", "gemini-1.5-flash-002", "gemini-1.5-pro-002"]

            model_name = None
            for p in preferred:
                if any(p in m for m in available):
                    model_name = p
                    break

            if not model_name:
                print("⚠️ No preferred model found. Using fallback: gemini-1.5-flash-002")
                model_name = "gemini-1.5-flash-002"

            print("✅ Using model:", model_name)
            self.model = genai.GenerativeModel(model_name=model_name)
            self.gemini_available = True
            
        except Exception as e:
            print(f"❌ Gemini AI setup failed: {e}")
            self.gemini_available = False
        
    def create_ui(self):
        # Header
        header = Label(self.root, text="GIPHY Upload Automation", 
                      font=("Arial", 18, "bold"), fg="#00FF9D", bg="#121212")
        header.pack(pady=20)
        
        # Instructions
        instructions = Label(self.root, 
                           text="This program will:\n1. Open GIPHY\n2. Guide you through the upload process\n3. Automate the file selection\n4. Add your name and generate tags",
                           font=("Arial", 12), fg="white", bg="#121212", justify="left")
        instructions.pack(pady=10)
        
        # Status display
        status_frame = Frame(self.root, bg="#1E1E1E", relief="solid", bd=1)
        status_frame.pack(pady=20, padx=40, fill="x")
        
        status_label = Label(status_frame, textvariable=self.status, 
                           font=("Arial", 11), fg="#00D8FF", bg="#1E1E1E", 
                           wraplength=400, justify="left", padx=10, pady=10)
        status_label.pack()
        
        # Button frame
        button_frame = Frame(self.root, bg="#121212")
        button_frame.pack(pady=20)
        
        # Start button
        start_btn = Button(button_frame, text="Start GIPHY Upload", 
                          font=("Arial", 12, "bold"), bg="#00FF9D", fg="black",
                          command=self.start_process, width=20, height=2)
        start_btn.pack(pady=10)
        
        # Gemini status
        gemini_status = "✅ Gemini AI Ready" if self.gemini_available else "❌ Gemini AI Not Available"
        gemini_label = Label(self.root, text=gemini_status,
                           font=("Arial", 10), fg="green" if self.gemini_available else "red", 
                           bg="#121212")
        gemini_label.pack(pady=5)
        
        # Warning
        warning = Label(self.root, 
                       text="Note: Do not move the mouse during automation!\nThe program will control your mouse and keyboard.",
                       font=("Arial", 10), fg="orange", bg="#121212", justify="center")
        warning.pack(pady=10)
        
    def update_status(self, message):
        self.status.set(message)
        self.root.update()
        
    def click_at_position(self, x, y, description):
        self.update_status(f"Step: {description}")
        pyautogui.click(x, y)
        time.sleep(1)
        
    def generate_and_paste_tags(self, topic):
        """Generate tags using Gemini AI and paste them"""
        if not self.gemini_available:
            self.update_status("Gemini AI not available - using default tags")
            default_tags = ["#gif", "#animation", "#funny", "#meme", "#trending", "#viral"]
            for tag in default_tags:
                pyperclip.copy(tag)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.2)
                pyautogui.press("enter")
                time.sleep(0.3)
            return
            
        try:
            self.update_status("Generating tags with AI...")
            
            # Generate tags dynamically
            prompt = f" do reseach a little on the topic i have given usually its a movie gather data and then Generate 14 short, SEO-friendly hashtags for {topic}. fisrt always include the name i have given , Only output the tags separated by commas. genrally searching movies indian and also have 1 tag for hero and another tag for herion any order is fine just have it and one dedicated tag which is most popular or viral "
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            tags = [tag.strip() for tag in text_response.replace("\n", "").split(",") if tag.strip()]
            
            if not tags:
                tags = ["#gif", "#animation", "#fun", "#trending", "#viral", "#meme"]
                
            print("\n✅ Tags generated:", tags)
            
            # Wait a moment before pasting
            time.sleep(1)
            
            # Paste tags one by one
            for tag in tags:
                pyperclip.copy(tag)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.2)
                pyautogui.press("enter")
                time.sleep(0.3)
                
            self.update_status("Tags successfully added!")
            
        except Exception as e:
            print(f"❌ Error generating tags: {e}")
            self.update_status("Error generating tags - using defaults")
            # Fallback to default tags
            default_tags = ["#gif", "#animation", "#fun", "#meme", "#trending", "#viral"]
            for tag in default_tags:
                pyperclip.copy(tag)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.2)
                pyautogui.press("enter")
                time.sleep(0.3)
    
    def start_process(self):
        self.update_status("Starting GIPHY upload process...")
        
        # Get user name at the beginning
        self.user_name = self.get_user_name()
        if not self.user_name:
            self.update_status("Process cancelled by user")
            return
            
        try:
            # Step 0: Open GIPHY website
            self.update_status("Opening GIPHY website...")
            url = "https://giphy.com/"
            webbrowser.open(url)
            time.sleep(5)  # Wait for page to load
            
            # Step 1: Click on upload button
            self.click_at_position(1229, 191, "Clicking on upload button")
            
            # Step 2: Click on file selection area
            self.click_at_position(705, 714, "Clicking on file selection area")
            
            # Step 3: Click on path input and paste the file path
            self.click_at_position(445, 167, "Clicking on path input")
            self.update_status("Pasting file path: C:\\Users\\harip\\ALL TEST")
            pyautogui.write("C:\\Users\\harip\\ALL TEST")
            pyautogui.press('enter')
            time.sleep(2)
            
            # Step 4: Click on search/name field and enter the name
            self.click_at_position(765, 165, "Clicking on name field")
            self.update_status(f"Entering name: {self.user_name}")
            pyautogui.write(self.user_name)
            time.sleep(5)  # Wait as specified
            
            # Step 5: Double click on the GIF selection and then Ctrl+A
            self.update_status("Double clicking and selecting all")
            pyautogui.doubleClick(574, 295)
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(1)
            
            # Step 6: Click on the upload confirmation
            self.click_at_position(770, 628, "Confirming selection")
            
            # Step 7: Wait 30 seconds for GIF to load
            self.update_status("Waiting 30 seconds for GIF to load...")
            for i in range(30, 0, -1):
                self.update_status(f"Waiting {i} seconds for GIF to load...")
                time.sleep(1)
            
            # Step 8: Click on tags area and generate/paste tags
            self.click_at_position(1211, 603, "Opening tags section")
            time.sleep(2)
            
            # Generate and paste tags using the same user name
            self.generate_and_paste_tags(self.user_name)
            
            # Step 9: Final upload click
            self.click_at_position(1257, 1035 ,"Final upload")
            
            self.update_status("Upload process completed successfully!")
            
        except pyautogui.FailSafeException:
            self.update_status("Process was aborted by moving mouse to corner")
        except Exception as e:
            self.update_status(f"An error occurred: {str(e)}")
    
    def get_user_name(self):
        return simpledialog.askstring("GIF Name", "Enter the name for your GIF:")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Check if required modules are installed
    try:
        import pyautogui
        import pyperclip
        app = GiphyUploader()
        app.run()
    except ImportError as e:
        print(f"Please install the required modules: pip install pyautogui pyperclip")
        print(f"Missing module: {e}")
        input("Press Enter to exit...")
