Adds a drop down option or context menu option to remove the background from an image, similar to the functionality seen in macOS. The current implementation may be slow for large images, but it works.

Run backgroundremover.pyw with the --register flag to add to your context menu. Use --unregister to remove it. 

Requires OpenCV- 

pip install opencv-python

To install:
python backgroundremover.pyw --register

To uninstall:
python backgroundremover.pyw --unregister

