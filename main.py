import math, struct, random, string
from pathlib import Path

"""
A breakdown:
First, this program takes a file and splits it into chunks, then distributes those chunks across multiple folders. Later, it can collect those chunks from the folders and reconstruct the original file.
Function breakdown: 
- pack: Packs a file into a binary format.
- unpack: Unpacks a file from its binary representation.
- save: Saves a file in a specified location.
- chunk_files: Finds the chunk files in a folder, hidden or not.
- get_them_folders: Gets a list of the folders in the specified path (hidden ones only if they hold chunks).
- split_data: Splits the data into chunks.
- distribute: Distributes the chunks across the folders, optionally hidden.
- collect_chunks: Collects the chunks from the folders and checks none are missing.
- recompact: Recompacts the chunks into a single data stream.
- construct: Constructs the original file from the distributed chunks.
- safe_construct: Calls construct but catches errors and exits with a short message.
- ask_path: Asks the user for a path and validates it.
- ask_foldgen: Asks the user how many folders to make and validates the number.
- make_them_folders: Makes the requested number of sub-folders, optionally hidden.
- folder_names: Generates names for the new folders.
- main: Runs the program and handles user input.
"""


FILE = b"storweird"

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
    """Save it somewhere normally. Not really weird but helpful for testing and me learning. Not used in the actual program."""
    packed = pack(path)
    destination.write_bytes(packed)

def chunk_files(folder):
    """Find the actual chunk files in a folder, now even if hidden."""
    return list(folder.glob("chunk_*.bin")) + list(folder.glob(".chunk_*.bin"))

def get_them_folders(path):
    """Get the number of folders in a path."""
    environment = Path(path)

    folders = [
      folder for folder in environment.iterdir()
        if folder.is_dir() and (not folder.name.startswith(".") or chunk_files(folder))
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

def distribute(chunks, folders, hidden=False):
    """Distribute the chunks across the folders."""
    if len(chunks) > len(folders):
        raise ValueError("Not enough folders to distribute the chunks.")

    saved_paths = []

    for i, (chunk,folder) in enumerate(zip(chunks, folders)):
        chunk_path = folder / f"{'.' if hidden else ''}chunk_{i}.bin"
        chunk_path.write_bytes(chunk)
        saved_paths.append(chunk_path)

    return saved_paths

def collect_chunks(folders):
    """Collect the chunks from the folders and output them."""
    chunks = []

    for folder in folders:
        chunks.extend(chunk_files(folder))

    chunks.sort(key=lambda c: int(c.stem.split("_")[1]))
    numbers = [int(c.stem.split("_")[1]) for c in chunks]
    if numbers != list(range(len(chunks))):
        raise ValueError(f"Missing chunks (or duplicates?). Oh no! We did find these chunks though: {numbers}.")

    return chunks

def recompact(chunks):
    """Recompact the chunks into a single thing, but does not touch them yet."""
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

def safe_construct(folders, dest):
    """Calls construct command but just catches errors if it does not work."""
    try:
        return construct(folders, dest)
    except (ValueError, OSError) as e:
        raise SystemExit(f"Couldn't rebuild: {e}")

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

def ask_foldgen(prompt, minimum=1, maximum=100):
    """Ask for the number of folders and keep asking until a good number is given."""
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and minimum <= int(raw) <= maximum:
            return int(raw)
        print ("Enter a number between 1 and 100. If you want more change the code.")

def make_them_folders(storage, count, hidden=False):
    """Make the sub-folders to store the chunks in inside the root storage folder."""
    made = []
    for name in folder_names(count):
        folder = storage / (("." +name) if hidden else name)
        folder.mkdir(exist_ok=True)
        made.append(folder)
    return made

def folder_names(count):
    """Generate random folder names."""
    if random.random() < 0.5:
        return [f"{chr(97 + i % 26)}{i // 26 or ''}" for i in range(count)]
    else:
        return [
            "".join(random.choices(string.ascii_lowercase, k=8))
            if random.choice([True, False])
            else f"{random.randrange(0x100000000):08x}"
            for _ in range(count)
        ]
    

def main():
    """Code that calls more code that calls more code once it is called."""
    while True:
        choice =  input("Split or reconstruct (s/r): ").strip().lower()
        if choice in ("s", "r"):
            break
        print("Please enter 's' to split or 'r' to reconstruct.")


    if choice == "s":
        src = ask_path("File to split: ")
        storage = ask_path("Folder containing the sub-folders (which you choose to generate) to store chunks in: ", want_dir=True)

        hidden = input("Make the chunks & new folders hidden? (y/n): ").strip().lower() == "y"
        folders = get_them_folders(storage)
        if not folders:
            if input("No sub-folders found. Make some? (y/n): ").strip().lower() != "y":
                raise SystemExit("No sub-folders to distribute into.")
            folders =make_them_folders(storage, ask_foldgen("How many sub-folders to make? (1-100): "),hidden)


        try:
            chunks = split_data(pack(src), len(folders))
            distribute(chunks, folders, hidden)
        except Exception as e:
            raise SystemExit(f"ERROR SPLITTING: {e}")
        print(f"Saved {len(chunks)} chunk(s) across {len(folders)} folder(s).")

        if input("Rebuild the file now? (y/n): ").strip().lower() == "y":
            dest = ask_path("Folder to restore the file into: ", want_dir=True)
            print("Rebuilt:", safe_construct(folders, dest))

    elif choice == "r":
        dest = ask_path("Folder to restore the file into: ", want_dir=True)
        storage = ask_path("Folder containing the sub-folders to collect chunks from: ", want_dir=True)

        folders = get_them_folders(storage)
        if not folders:
            raise SystemExit("That folder has no sub-folders to collect from.")

        print("Rebuilt:", safe_construct(folders, dest))

        if input("Would you like to clear the old chunks (keeps the folders)? (y/n): ").strip().lower() == "y":
            for folder in folders:
                for chunk in chunk_files(folder):
                    chunk.unlink()
            print("Old chunks cleared.")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n):")