import os
import json

ROOTS = {"article": "artikel"}
SNIPPET_LENGTH = 200

index = {}

for type_, root in ROOTS.items():
    for year in os.listdir(root):
        year_path = os.path.join(root, year)
        if not os.path.isdir(year_path):
            continue

        if year not in index:
            index[year] = {}

        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path):
                continue

            if month not in index[year]:
                index[year][month] = {}

            for day in os.listdir(month_path):
                day_path = os.path.join(month_path, day)
                if not os.path.isdir(day_path):
                    continue

                if day not in index[year][month]:
                    index[year][month][day] = {}

                for file in os.listdir(day_path):
                    if not file.endswith(".json"):
                        continue
                    filepath = os.path.join(day_path, file)
                    file_id = os.path.splitext(file)[0]  # Use filename as key

                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content_json = json.load(f)
                            content_text = content_json.get("content", "")
                    except Exception as e:
                        content_text = ""
                        print(f"Failed to read {filepath}: {e}")

                    # Extract title from first Markdown heading
                    lines = content_text.splitlines()
                    title_found = None
                    snippet_lines = []
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith("#") and title_found is None:
                            title_found = line.lstrip("#").strip()
                        else:
                            snippet_lines.append(line)

                    snippet = " ".join(snippet_lines)
                    snippet = snippet[:SNIPPET_LENGTH] + ("..." if len(snippet) > SNIPPET_LENGTH else "")

                    index[year][month][day][file_id] = {
                        "title": title_found if title_found else file_id,
                        "date": f"{year}-{month}-{day}",
                        "path": filepath,
                        "snippet": snippet
                    }

# Save to JSON
with open("pageindex.json", "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print("Nested JSON by ID created successfully.")
