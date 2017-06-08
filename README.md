# image-clipper

##### Simple image clipper that has been made for manual data set preparation.

```
Usage: image-clipper.py path_to_folder path_for_save position_to_start save_number show_clipped open_grayscale histogram_equalization final_width final_height
```

```
Example: image-clipper.py ./data_set ./clips 1 1 True False False -1 -1
```

If you press **ESC**, next file number and next saved number  
in saved folder will be displayed and program will terminate.  
You can use these values to continue your clipping further.

For example,  
Next file number: 4.  
Next saved number: 7.  
You can use these values: **image-clipper.py** *./data_set* *./clips* *4* *7* *True* *False* *False* *-1* *-1*

If you don't want to scale clips then, use -1 for *final_width* *final_height*.

Requirements:
- Python 3;
- OpenCV3;
- <a href="https://github.com/dicompyler/dicompyler-core" target="_blank">dicompyler-core</a> (Optionally, if you need dicom support).
