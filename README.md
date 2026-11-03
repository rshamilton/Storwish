# Storwish
A Python program that splits a file into a bunch of binary files, one per folder in the directory given.

## Requirements
Python 3 and your terminal. Nothing else needs to be installed.

## Usage
- Run main.py (python main.py or python3 main.py on MacOS)
- Choose a mode. You can't reconstruct files if you haven't split one yet!

### If splitting:
- Enter the path to the intended file to split in standard format: ~/Documents/ExampleFolder/Image.anything
- Enter the path to the folder containing subdirectories to split the file into: ~/Documents/ExampleFolder
- Choose whether or not to hide folders and chunks (just adds a '.' to the beginning of the file name)
- If no subfolders are found, choose whether to create some, then select an amount (1-100)
- Choose whether to rebuild the file right away. If yes, enter the path to the folder where it should land

### If reconstructing:
- Enter the path to where you want the reconstructed file to land: ~/Documents/ExampleFolder
- Enter the path to the folder containing subdirectories to collect chunks from: ~/Documents/ExampleFolder
- Choose if you want to delete the old chunks

## Notes
- Only folders the program creates get hidden. Existing folders keep their names, but the chunks inside them are hidden
- Splitting overwrites existing chunk files, and rebuilding overwrites a file with the same name in the folder you pick
- File names longer than 255 bytes aren't allowed
