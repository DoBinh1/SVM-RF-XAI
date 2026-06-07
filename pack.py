import sys
import os
import zipfile
import argparse

def main():
    parser = argparse.ArgumentParser(description="Pack directory to pptx")
    parser.add_argument("src_dir", help="Source directory")
    parser.add_argument("dest_pptx", help="Destination pptx file")
    parser.add_argument("--original", help="Original pptx file (optional)", default=None)
    args = parser.parse_args()
    
    src_dir = args.src_dir
    dest_pptx = args.dest_pptx
    
    with zipfile.ZipFile(dest_pptx, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, src_dir)
                zip_ref.write(file_path, arcname)
    print(f"Packed {src_dir} to {dest_pptx}")

if __name__ == '__main__':
    main()
