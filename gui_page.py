import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image
import audio_processing_cepstral as apc
from numpy import float64
import threading
import Speedometer as sm

NOTES_FREQUENCIES = {
    'E1': 82.41,
    'A': 110.00,
    'D': 146.83,
    'G': 196.00,
    'B': 246.94,
    'E6': 329.63,

}

FREQUENCIES = {
    'E1': 82.41,#324.26517155310506 ,
    'A': 110.00,#630.0008979078747
    'D': 146.83,#512.7914401972141,
    'G': 98.00044444444447,#588.00,#612.5008937508936 
    'B': 125.28429543818312,
    'E6': 165.78972599283443,

}

#Global constants
SAMPLE_RATE = 44100  
DURATION = 5 

#Global variables for String Selection
is_toggled=0
frequency_selected = 0
string_selected = ""
key_button_dict = {}

#Global variables for Thread / Application Closure
record_thread = None
busy_processing = False
close_requested = False

#Function called on closing the window
def close_window():
    global close_requested
    close_requested = True
    app.destroy()

#Function called fpr toggling other buttons while recordng and analyzing a string note for deviation
def toggle_button_status():
  global is_tog    
  if (is_toggled):
    for keys in key_button_dict:
      if keys != string_selected:
        key_button_dict[keys].configure(state="disabled", fg_color="grey")
  else: # Enable all buttons
    for keys in key_button_dict:
        key_button_dict[keys].configure(state="normal", fg_color="Black")

# Thread Function -- this executes a while  loop to record and analyze string note fpr deviation
# if Stop button is clicked or application is closed, the while loop exits and the thread stops  
def record_fn():
  global is_toggled, frequency_selected, busy_processing
  print("inside record function", "ïs toggled = ", is_toggled)
  while(True):
    if(is_toggled and not close_requested):
      busy_processing = True
      audio_signal, wav_file = apc.record_audio(DURATION, SAMPLE_RATE, 2, float64)
      deviation_perc, deviation, return_status, return_string =apc.find_deviation_ceps(wav_file,frequency_selected, SAMPLE_RATE)
      # If Application is closed while recording, do not display deviation result
      if (not close_requested):
        if (return_status != "Skip"):
          if (return_status == "In Tune" ):
            #display_deviation_label1.configure(text=return_status)
            display_deviation_label1.configure(image=tick_image)  
          else : 
            display_deviation_label1.configure(image=wrong_image)
            
          display_deviation_label2.configure(text=return_string)
          display_deviation_label1.update()
          display_deviation_label2.update()
          speedometer.update_needle(deviation_perc)
    else:#Stops the Thread
      busy_processing = False
      record_thread = None
      break  

#Function called to create a thread on record button click
def record_threading_fn(action="START" ):
  global record_thread
  record_thread=threading.Thread(target=record_fn)
  record_thread.start()

#Function called on Click of Record and Analyze Button
def button_click(key):
  global frequency_selected, string_selected
  string_selected = key
  frequency_selected=FREQUENCIES[key]
  # Form the String to Display the selected Frequency
  display_std_freq = f"{frequency_selected:.2f}"+"Hz"
  display_string_label1.configure(text=key)
  display_string_label1.update()
  display_string_label2.configure(text=display_std_freq)
  display_string_label2.update()
  
  #Start the thread for Recording and analyzing the audio
  record_threading_fn("START")

#Toggles the configuration of the button
def toggle(button,key):
  global is_toggled
  
  if is_toggled:
    #record_threading_fn("STOP")
    button.configure(text=key,fg_color="#9DBBAE")
  else: #Start Recording
    button.configure(text="Stop", fg_color="#9DBBAE")
    button_click(key)
  is_toggled=not is_toggled
  #Enables / Disables the other Buttons to prevent user from selecting other strings when recording is going on
  toggle_button_status()

# Create the Application Main Window and set its properties
ctk.set_appearance_mode("system")
# Selecting color theme-blue, green, dark-blue
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
#Set the Call Back for application closure
app.protocol("WM_DELETE_WINDOW", close_window)

# Set the application properties
app.geometry("600x600")
app.title("Guitar Tuner")
app.resizable(False, False)
openstack_icon = app.iconbitmap('guitar.ico')

#Split the screen into 2 Outer Frames - One for Buttons and Guitar - Second for Displaying Deviation
outer_frame_1=ctk.CTkFrame(app, width=600,height=400, fg_color="#A3BCF9")
#outer_frame_1.grid(row=0, column=0, sticky="NE")
outer_frame_1.pack(fill="both", expand=True)

outer_frame_2=ctk.CTkFrame(app, width=600,height=200, fg_color="#A3BCF9")
#outer_frame_2.grid(row=1, column=0, sticky = "NE")
outer_frame_2.pack(fill="both", expand=True)


# Create a Left Button frame 
button_frame_left=ctk.CTkFrame(outer_frame_1, width=100,height=400, fg_color="#647BC5")
button_frame_left.grid(row=0, column=0, sticky="NE")

# Create a Center frame for holding the guitar image
frame = ctk.CTkFrame(outer_frame_1, width=400, height=400, fg_color="#C9CAD9")
frame.grid(row=0, column=1)

# Create a Right Button frame 
button_frame_right=ctk.CTkFrame(outer_frame_1, width=100, height=400, fg_color="#647BC5")
button_frame_right.grid(row=0, column=2)

# Create 3 Frames in Outer Frame 2 to display the deviation and speedometer 
display_frame1=ctk.CTkFrame(outer_frame_2, width=175, height=200, fg_color="#7796CB")
display_frame1.pack(fill="both", expand=True, side="left")
#display_frame1.grid(row=0, column=0, sticky="NE")

#Speedometer Frame
speedometer_frame = ctk.CTkFrame(outer_frame_2, width=250, height=200, fg_color="#A3BCF9")
#speedometer_frame.grid(row=0, column=1)
speedometer_frame.pack(fill="both", expand=True, side="left")

#display Deviation as percentage and recorded Deviation
display_frame2=ctk.CTkFrame(outer_frame_2, width=175, height=200, fg_color="#7796CB")
#display_frame2.grid(row=0, column=2)
display_frame2.pack(fill="both", expand=True, side="left")

#Create speedometer
speedometer = sm.Speedometer(speedometer_frame, width=220, height=220)
#speedometer.pack(fill="both", expand=True, anchor="center" )
#speedometer.grid(row=0, column=0, sticky="center")
speedometer.place(relx=0.2, rely=0.2)

# Create a label to display the String selected and its frequency
font_tmp = ctk.CTkFont("Helvetica", size=15, weight="bold")
display_label1 = ctk.CTkLabel(display_frame1, width=150, height= 40, text="String Selected   :  ", fg_color= "#C9CAD9", anchor="w", font=font_tmp)
display_label1.place(relx=0.07, rely=0.10)
display_string_label1 = ctk.CTkLabel(display_frame1, width=150, height= 40, text="                       ", fg_color= "#D1D2F9", anchor="w", font=font_tmp)
display_string_label1.place(relx=0.07, rely=0.30)
display_label2 = ctk.CTkLabel(display_frame1, width=150, height= 40, text="Standard Frequency : ", fg_color= "#C9CAD9", anchor="w", font=font_tmp)
display_label2.place(relx=0.07, rely=0.50)
display_string_label2 = ctk.CTkLabel(display_frame1, width=150, height= 40, text="                       ", fg_color= "#D1D2F9", anchor="w", font=font_tmp)
display_string_label2.place(relx=0.07, rely=0.70)


# Create a label to display the String selected and its frequency
display_label3 = ctk.CTkLabel(display_frame2, width=150, height= 40, text="Result : ", fg_color= "#C9CAD9", anchor="w", font=font_tmp)
display_label3.place(relx=0.07, rely=0.10)
display_deviation_label1 = ctk.CTkLabel(display_frame2, width=150, height= 40, text="     ", fg_color= "#D1D2F9", anchor="w", font=font_tmp)
display_deviation_label1.place(relx=0.07, rely=0.30)
display_label4 = ctk.CTkLabel(display_frame2, width=150, height= 40, text="Deviation  : ", fg_color= "#C9CAD9", anchor="w", font=font_tmp)
display_label4.place(relx=0.07, rely=0.50)
display_deviation_label2 = ctk.CTkLabel(display_frame2, width=150, height= 40, text="", fg_color= "#D1D2F9", anchor="w", font=font_tmp)
display_deviation_label2.place(relx=0.07, rely=0.70)


# Create Image object for the centre guitar picture
cwd = os.getcwd()
file_path = os.path.join(cwd, "headstock_image.png")

original_img=Image.open(file_path)
resized_image = original_img.resize((400, 400))
guitar_image = ctk.CTkImage(light_image=resized_image, size=(400, 400))

file_path = os.path.join(cwd, "Tick_Icon.png")
original_tick_img=Image.open(file_path)
resized_tick_image = original_tick_img.resize((40, 40))
tick_image = ctk.CTkImage(light_image=resized_tick_image, size=(40, 40))

file_path = os.path.join(cwd, "Wrong_Icon.png")
original_wrong_img=Image.open(file_path)
resized_wrong_image = original_wrong_img.resize((40, 40))
wrong_image = ctk.CTkImage(light_image=resized_wrong_image, size=(40, 40))

# Create a label to hold the image in the center frame
label = ctk.CTkLabel(frame, image=guitar_image)
label.pack(fill="both", expand=True)

 
# Create the String Buttons on the Left Frame
button_e1=ctk.CTkButton(button_frame_left,  width = 50, height = 50, corner_radius = 5, text="E1",fg_color="Black",text_color="#C9CAD9",command=lambda:toggle(button_e1,"E1"))
#button_e1.grid(row=0,column=0, padx=30, pady=63)
button_e1.place(relx=0.25, rely= 0.18)
key_button_dict["E1"]=button_e1

button_a=ctk.CTkButton(button_frame_left,width = 50, height = 50, corner_radius = 5, text="A",fg_color="Black",text_color="#C9CAD9",command=lambda:toggle(button_a,"A"))
#button_a.grid(row=1,column=0, padx=30, pady=30)
button_a.place(relx=0.25, rely= 0.36)
key_button_dict["A"]=button_a

button_d=ctk.CTkButton(button_frame_left, width = 50, height = 50, corner_radius = 5,text="D",fg_color="Black",text_color="#C9CAD9",command=lambda:toggle(button_d,"D"))
#button_d.grid(row=2,column=0, padx=30, rowspan= 2, pady=63)
button_d.place(relx=0.25, rely= 0.54)
key_button_dict["D"]=button_d

# Create the String Buttons on the Right Frame
button_g=ctk.CTkButton(button_frame_right, width = 50, height = 50, corner_radius = 5,text="G",fg_color="Black",text_color="#C9CAD9",command=lambda:toggle(button_g,"G"))
#button_g.grid(row=0, column=0, padx=30, pady=30)
button_g.place(relx=0.25, rely= 0.18)
key_button_dict["G"]=button_g

button_b=ctk.CTkButton(button_frame_right,width = 50, height = 50, corner_radius = 5,text="B",fg_color="black", text_color="#C9CAD9",command=lambda:toggle(button_b,"B"))
#button_b.grid(row=1, column=0, padx=30, pady=30)
button_b.place(relx=0.25, rely= 0.36)
key_button_dict["B"]=button_b

button_e6=ctk.CTkButton(button_frame_right,width = 50, height = 50, corner_radius = 5,text="E6",fg_color="Black", text_color="#C9CAD9",command=lambda:toggle(button_e6,"E6"))
#button_e6.grid(row=2, column=0, padx=30, pady=30)
button_e6.place(relx=0.25, rely= 0.54)
key_button_dict["E6"]=button_e6

#Run the Application
app.mainloop()