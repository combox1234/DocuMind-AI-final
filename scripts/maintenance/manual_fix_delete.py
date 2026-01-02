"""
Directly fix the delete_file function in app.py - manual replacement
"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line "# Handle files in both incoming and sorted directories"
# and replace the logic from there until "if not full_path.exists()" 

start_marker = "        # Handle files in both incoming and sorted directories\n"
end_marker = "        if not full_path.exists():\n"

try:
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if line == start_marker and start_idx is None:
            start_idx = i
        if line == end_marker and start_idx is not None and end_idx is None:
            end_idx = i
            break
    
    if start_idx and end_idx:
        # New logic to insert
        new_logic = [
            "        # Handle files in both incoming and sorted directories\n",
            "        sorted_dir = Config.SORTED_DIR\n",
            "        incoming_dir = Config.INCOMING_DIR\n",
            "        \n",
            "        # Handle different file locations\n",
            "        if filepath.startswith('incoming/'):\n",
            "            # File is marked as still processing\n",
            "            filename = filepath.replace('incoming/', '')\n",
            "            \n",
            "            # Try incoming directory first\n",
            "            full_path = incoming_dir / filename\n",
            "            is_incoming = True\n",
            "            \n",
            "            # If not in incoming, search in sorted (*worker processed but DB not updated*)\n",
            "            if not full_path.exists():\n",
            "                # Search for file in sorted directory\n",
            "                import glob\n",
            "                pattern = str(sorted_dir / '**' / filename)\n",
            "                matches = glob.glob(pattern, recursive=True)\n",
            "                \n",
            "                if matches:\n",
            "                    from pathlib import Path\n",
            "                    full_path = Path(matches[0])\n",
            "                    is_incoming = False  # Actually sorted\n",
            "                else:\n",
            "                    return jsonify({'error': 'File not found'}), 404\n",
            "        else:\n",
            "            # File is in sorted directory\n",
            "            full_path = sorted_dir / filepath\n",
            "            is_incoming = False\n",
            "            \n",
            "            # Security check - ensure path is within sorted directory\n",
            "            if not str(full_path.resolve()).startswith(str(sorted_dir.resolve())):\n",
            "                return jsonify({'error': 'Invalid file path'}), 400\n",
            "        \n",
        ]
        
        # Replace lines from start_idx to end_idx with new_logic
        lines = lines[:start_idx] + new_logic + lines[end_idx:]
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("SUCCESS: Fixed delete_file function")
        print(f"Replaced lines {start_idx+1} to {end_idx+1}")
        print("Delete now searches for files in sorted directory")
    else:
        print(f"ERROR: Could not find markers. start={start_idx}, end={end_idx}")
        
except Exception as e:
    print(f"ERROR: {e}")
