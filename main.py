import math, struct
from pathlib import Path

"""
A breakdown:
First, this program takes a file and splits it into chunks, then distributes those chunks across multiple folders. Later, it can collect those chunks from the folders and reconstruct the original file.
Function breakdown: 
- pack: Packs a file into a binary format.
- unpack: Unpacks a file from its binary representation.
- save: Saves a file in a specified location.
- get_them_folders: Gets the number of folders in a path.
- split_data: Splits the data into chunks.
- distribute: Distributes the chunks across the folders.
- collect_chunks: Collects the chunks from the folders.
- recompact: Recompacts the chunks into a single data stream.
- construct: Constructs the original file from the distributed chunks.
"""


FILE = b"This is a completely random string that formats my files, apparently. How interesting."

def pack(path):
    data = path.read_bytes() 
    name = path.name.encode() #Makes the name binary too
    if len(name) > 255:
        raise ValueError("File name too long. This is weird, I know, since this is supposed to be weird.")
    header = FILE + struct.pack("<BI", len(name), len(data)) + name
    return header + data

def unpack(it):
    """Unpack a file from its binary representation."""
    if it[:len(FILE)] != FILE:
        raise ValueError("Invalid file format.")
    name_len, data_len = struct.unpack("<BI", it[len(FILE):len(FILE)+5])
    name = it[len(FILE)+5:len(FILE)+5+name_len].decode()
    data = it[len(FILE)+5+name_len:len(FILE)+5+name_len+data_len]
    if len(data) != data_len:
        raise ValueError("Something went wrong.")
    return name, data

def save(path, destination):
    """Save it somewhere normally. Not really weird but helpful for testing and me learning."""
    packed = pack(path)
    destination.write_bytes(packed)

def get_them_folders(path):
    """Get the number of folders in a path."""
    environment = Path(path)

    folders = [
      folder for folder in environment.iterdir()
        if folder.is_dir()
    ]
    return folders

def split_data(data, folders_available):
    if not data:
        return []
    chunk_size = math.ceil(len(data) / folders_available)
    print(f"Chunk size: {chunk_size} bytes split across {folders_available} folders.")

    chunks = []

    for i in range(0,len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        chunks.append(chunk)
    return chunks

def distribute(chunks, folders):
    """Distribute the chunks across the folders."""
    if len(chunks) > len(folders):
        raise ValueError("Not enough folders to distribute the chunks.")

    saved_paths = []

    for i, (chunk,folder) in enumerate(zip(chunks, folders)):
        chunk_path = folder / f"chunk_{i}.bin"
        chunk_path.write_bytes(chunk)
        saved_paths.append(chunk_path)

    return saved_paths

def collect_chunks(folders):
    """Collect the chunks from the folders and output them."""
    chunks = []

    for folder in folders:
        chunks.extend(folder.glob("chunk_*.bin"))

    # Sort numerically across all folders so chunk_2 comes before chunk_10
    # and folder listing order doesn't matter
    chunks.sort(key=lambda c: int(c.stem.split("_")[1]))

    return chunks

def recompact(chunks):
    data = b""

    for chunk in chunks:
        data += chunk.read_bytes()

    return data

def construct(folders, destination):
    """Construct the original file from the distributed chunks."""
    chunks = collect_chunks(folders)
    packed_data = recompact(chunks)
    name, data = unpack(packed_data)

    output_path = destination / name
    output_path.write_bytes(data)

    return output_path


def ask_path(prompt, must_exist=True, want_dir=False):
    """Keep asking until the user gives a usable path."""
    while True:
        raw = input(prompt).strip().strip("'\"")
        path = Path(raw).expanduser()
        if not raw:
            print("Please enter a path.")
        elif must_exist and not path.exists():
            print(f"Not found: {path}")
        elif want_dir and path.exists() and not path.is_dir():
            print(f"Not a folder: {path}")
        elif not want_dir and must_exist and not path.is_file():
            print(f"Not a file: {path}")
        else:
            return path


"""Actual code that runs. Finally."""

if __name__ == "__main__":
    while True:
        choice =  input("Split or reconstruct (s/r): ").strip().lower()
        if choice in ("s", "r"):
            break
        print("Please enter 's' to split or 'r' to reconstruct.")


    if choice == "s":
        src = ask_path("File to split: ")
        storage = ask_path("Folder containing the sub-folders to store chunks in: ", want_dir=True)

        folders = get_them_folders(storage)
        if not folders:
            raise SystemExit("That folder has no sub-folders to distribute into.")

        chunks = split_data(pack(src), len(folders))
        distribute(chunks, folders)
        print(f"Saved {len(chunks)} chunk(s) across {len(folders)} folder(s).")

        if input("Rebuild the file now? (y/n): ").strip().lower() == "y":
            dest = ask_path("Folder to restore the file into: ", want_dir=True)
            print("Rebuilt:", construct(folders, dest))

    elif choice == "r":
        dest = ask_path("Folder to restore the file into: ", want_dir=True)
        storage = ask_path("Folder containing the sub-folders to collect chunks from: ", want_dir=True)

        folders = get_them_folders(storage)
        if not folders:
            raise SystemExit("That folder has no sub-folders to collect from.")

        print("Rebuilt:", construct(folders, dest))

        if input("Would you like to clear the old chunks? (y/n): ").strip().lower() == "y":
            for folder in folders:
                for chunk in folder.glob("chunk_*.bin"):
                    chunk.unlink()
            print("Old chunks cleared.")