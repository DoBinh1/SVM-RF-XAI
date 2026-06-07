import sys
import os
import zipfile

def main():
    if len(sys.argv) < 3:
        print("Usage: python unpack.py <input.pptx> <output_dir>")
        sys.exit(1)
    
    pptx_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"Unpacked {pptx_path} to {output_dir}")

if __name__ == '__main__':
    main()
