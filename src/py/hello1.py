#!/usr/bin/env python


# This tells Python to load the Gimp module 
from gimpfu import *

# This is the function that will perform actual actions
def my_script_function(image, drawable, text_value, int_value) :
    print "Hello from my script!"
    print "You sent me this text: "+text_value
    print "You sent me this number: %d"%int_value
    return

# This is the plugin registration function
register(
    "my_first_script",    
    "My first Python-Fu",   
    "This script does nothing and is extremely good at it",
    "Michel Ardan", 
    "Michel Ardan Company", 
    "April 2010",
    "<Image>/MyScripts/My First Python-Fu", 
    "*", 
    [
      (PF_STRING, 'some_text', 'Some text input for our plugin', 'Write something'),
      (PF_INT, 'some_integer', 'Some number input for our plugin', 2010)
    ], 
    [],
    my_script_function,
    )

main()
