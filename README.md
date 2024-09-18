
 # TXTure
======

 ## Surgically edit machine-readable ASCII files

 ![image](https://github.com/user-attachments/assets/1d95a193-7db6-4359-8511-19b29e3f5c17)


TXTure Provides intuitive ways  to work with data in text files

Below are the basic primitives used.  
By convention:  

 lines is a list of strs  previously read in from a text file  
def read(txtfile):  
    return txtfile.read_text(errors='ignore').split('\n')    

a key is a str or list of strs  specifying where to  search within lines  from the text file 

a list  is used to search for each str in sequence, and stop once it finds the last key  
either the line index of the last key, the full line content, or the  part of the line's str  that comes after the key may be important  

a seq, or sequence, Is a group of lines  that all start with the same key,  for example:  
Plan File=p01  
Plan File=p03  
Plan File=p04  
Plan File=p02  

 a block is a  continuous partition of lines,  delimited by  line indeces found at 2 keys  




* Free software: MIT license
* Documentation: https://TXTure.readthedocs.io.
