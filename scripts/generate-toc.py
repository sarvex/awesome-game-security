filename = "../README.md"
insert_line = 3

indent_lookup = {
    '## ': 0,
    '### ': 1, # unused right now
    '#### ': 2, # unused right now
}


found_items = []

with open(filename, "r") as f:
    readme_lines = f.readlines()
for line in readme_lines:
    for prefix, value in indent_lookup.items():
        if line.startswith(prefix):
            heading = line[len(prefix):].strip()
            heading_ref = heading.replace(' ', '-')
            found_items.append('%s- [%s](#%s)' % ('\t' * value, heading, heading_ref))
for item in found_items:
    print(item)

readme_lines.insert(insert_line, '## Contents\n')

for i in range(len(found_items)):
    item = found_items[i]
    readme_lines.insert(insert_line + i + 1, item + '\n')
readme_lines.insert(insert_line + len(found_items) + 1, '\n')

with open(filename, "w") as f:
    f.writelines(readme_lines)
