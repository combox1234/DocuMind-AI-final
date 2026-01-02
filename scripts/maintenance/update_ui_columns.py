"""
Update index.html and main.js to add Uploaded By column (without unicode chars)
"""

# Fix index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add Uploaded By header
html = html.replace(
    '<th>Size</th>\n                            <th>Actions</th>',
    '<th>Size</th>\n                            <th>Uploaded By</th>\n                            <th>Actions</th>'
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html with Uploaded By column header")

# Fix main.js
with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Update colspan for empty message
js = js.replace('colspan="5"', 'colspan="6"')

# Update file row template to include uploaded_by
old_template = '''        tbody.innerHTML = filesData.files.map(file => {
            const sizeKB = (file.size / 1024).toFixed(2);
            return `
                <tr>
                    <td>${file.filename}</td>
                    <td><span class="file-chip">${file.domain}</span></td>
                    <td><span class="tag">${file.category}</span></td>
                    <td>${sizeKB} KB</td>
                    <td>
                        <button class="btn-danger" style="padding: 4px 12px; font-size: 13px;" 
                            onclick="deleteUserFile('${file.path.replace(/\\\\/g, '\\\\\\\\')}', '${file.filename}')">
                            Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join('');'''

new_template = '''        tbody.innerHTML = filesData.files.map(file => {
            const sizeKB = (file.size / 1024).toFixed(2);
            const uploadedBy = file.uploaded_by || 'Unknown';
            return `
                <tr>
                    <td>${file.filename}</td>
                    <td><span class="file-chip">${file.domain}</span></td>
                    <td><span class="tag">${file.category}</span></td>
                    <td>${sizeKB} KB</td>
                    <td>${uploadedBy}</td>
                    <td>
                        <button class="btn-danger" style="padding: 4px 12px; font-size: 13px;" 
                            onclick="deleteUserFile('${file.path.replace(/\\\\/g, '\\\\\\\\')}', '${file.filename}')">
                            Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join('');'''

js = js.replace(old_template, new_template)

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Updated main.js with Uploaded By column")
print("All updates complete!")
