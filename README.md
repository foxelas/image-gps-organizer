# image-date-fixer
 A simple python script and .exe file that sorts images based on GPS metadata.

Input a folder (with all subfolders) into a file. It will check if there is GPS metadata, and if there is, it will move it to a folder and add the island and the group to its name.**

The final folder will have the format:
\[Photos {Saronic/Sporades/Ionio/Cyclades/Dodecanese(Island/Area)}\]

So, the DJI_0001 photo taken in Kleftiko on Milos will be renamed to DJI_0001_Cyc_Milos and placed in the folder:
Photos - Cyclades - Milos

A file with location and date tracker is saved in location_tracker.csv
