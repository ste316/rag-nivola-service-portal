from os import rmdir, unlink, listdir
from os.path import exists, join

def delete_all_chat():
    directory = 'pages'
    try:
        # Check if the directory exists
        if exists(directory):
            # Remove all files in the directory
            for filename in listdir(directory):
                file_path = join(directory, filename)
                try:
                    # Remove the file
                    unlink(file_path)
                    print(f"Successfully deleted file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

            # Remove the directory itself
            rmdir(directory)
            print(f"Successfully deleted directory: {directory}")
    except Exception as e:
        print(f"Failed to delete directory: {directory}. Reason: {e}")

if __name__ == '__main__':
    delete_all_chat()