import os

def write_dir_to_file(directory=".", output_file="file_list.txt"):
    try:
        # Get list of files
        files = os.listdir(directory)
        
        # Open the text file with UTF-8 encoding to support Hindi
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Directory listing for: {os.path.abspath(directory)}\n")
            f.write("="*50 + "\n\n")
            
            for filename in files:
                f.write(filename + "\n")
                
        print(f"Success! List saved to '{output_file}'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    write_dir_to_file(".")