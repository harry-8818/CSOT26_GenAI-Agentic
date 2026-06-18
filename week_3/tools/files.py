import os
import difflib

def list_files(directory=".") :
    try :
        files = os.listdir(directory)
        return str(files)
    except Exception as e:
        return f"[ERROR]: Not able to list the files because {str(e)}"
    
def read_file(file_path):
    try :
        with open(file_path,"r",encoding="utf-8") as f :
            content = f.read()
            return content[:10000]
    except Exception as e:
        return f"[ERROR]: Not able to read the file because {str(e)}"

def write_file(file_path,content):
    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent,exist_ok=True)
    try :
        with open(file_path,"w",encoding="utf-8") as f :
            f.write(content)
            return "Writing the contents in the file was successful."
    except Exception as e:
        return f"[ERROR]: Not able to write the contents in the file because {str(e)}"

def edit_file(file_path,old_content,new_content):
    try :
        with open(file_path,"r",encoding="utf-8") as f :
            old_full_content = f.read()
            if (old_content not in old_full_content) :
                return "[ERROR]: Not able to find the target text to be edited."  
            new_full_content = old_full_content.replace(old_content,new_content,1)
            diff = difflib.unified_diff(old_full_content.splitlines(keepends=True),new_full_content.splitlines(keepends=True),
                                        fromfile=f"Original_{os.path.basename(file_path)}",tofile=f"Updated_{os.path.basename(file_path)}",n=3)
            changes = "".join(diff)
        with open(file_path,"w",encoding="utf-8") as f :
            f.write(new_full_content)
        return f"Successfully edited the file.\n\nChanges:\n{changes}\n"
    except Exception as e:
        return f"[ERROR]: Not able to edit the file because {str(e)}"                
    
file_tools_schema = [{
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "Returns a list of all files in a specified directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The directory path to list files from, e.g., '.'"
                }
            },
            "required": ["directory"]
        }
    }
},
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the text content of a specified file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The exact path or name of the file to read."
                    }
                },
                "required": ["file_path"]
            }
        }
},
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes text to a file, creating it if it doesn't exist or overwriting it if it does.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The name or path of the file to write to."
                    },
                    "content": {
                        "type": "string",
                        "description": "The exact text content to write inside the file."
                    }
                },
                "required": ["file_path", "content"]
            }
        }
},
{
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edits a file using a strict find-and-replace. To REPLACE: provide old and new text. To DELETE: provide old text and leave new_content completely empty. To APPEND: make old_content the last line of the file, and make new_content that same last line followed by a newline (\\n) and the new text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The exact name or path of the file to edit."
                    },
                    "old_content": {
                        "type": "string",
                        "description": "The exact block of content currently inside the file that needs to be targeted. Must match spacing and indents perfectly."
                    },
                    "new_content": {
                        "type": "string",
                        "description": "The new content to swap in. Leave empty to delete. Include the old_content plus new text to append."
                    }
                },
                "required": ["file_path", "old_content", "new_content"]
            }
        }
    }]