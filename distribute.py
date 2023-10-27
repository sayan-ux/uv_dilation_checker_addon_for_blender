import os
import tempfile
import shutil
import zipfile

# Step 1: Create a temporary build folder
build_dir = tempfile.mkdtemp()
print(f"Created temporary build folder: {build_dir}")

# Step 2: Copy "uv_dilation_checker.py" to the build folder
source_file = "uv_dilation_checker.py"
destination_file = os.path.join(build_dir, "uv_dilation_checker.py")
shutil.copy(source_file, destination_file)
print(f"Copied {source_file} to {destination_file}")

# Step 3: Install dependencies in the "deps" folder
deps_dir = os.path.join(build_dir, "deps")
os.makedirs(deps_dir)
requirements_file = "requirements.txt"
os.system(f"pip install -r {requirements_file} -t {deps_dir}")
print(f"Installed dependencies in the 'deps' folder")

# Step 4: Copy the "cv2" folder from "deps" to the build folder
cv2_dir = os.path.join(deps_dir, "cv2")
if os.path.exists(cv2_dir):
    shutil.copytree(cv2_dir, os.path.join(build_dir, "cv2"))
    print(f"Copied 'cv2' folder to the build folder")

# Step 5: Delete the "deps" folder
shutil.rmtree(deps_dir)
print(f"Deleted the 'deps' folder")

# Step 6: Zip the folder
output_zip = "uv_dilation_checker.zip"
with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for foldername, subfolders, filenames in os.walk(build_dir):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            zipf.write(filepath, os.path.relpath(filepath, build_dir))

print(f"Zipped build folder to {output_zip}")

# Step 7: Clean up the temporary build folder
shutil.rmtree(build_dir)
print(f"Cleaned up the temporary build folder: {build_dir}")
