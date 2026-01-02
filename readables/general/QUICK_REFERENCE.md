# 🚀 Quick Reference - Hierarchical Classification

## File Path Structure
```
sorted/
├── {Domain}/
│   ├── {Category}/
│   │   ├── {FileType}/
│   │   │   └── filename.ext
```

## Example Paths
```
Technology/UAV/pptx/UAV_Technology.pptx
Finance/Maintenance/xlsx/Maintenance_2024.xlsx
College/Clubs/pdf/CS_Club_Meeting.pdf
Education/Programming/py/Python_OOP_Module3.py
Company/Product/md/Product_Spec_v2.md
School/Assignments/pdf/Math_Homework_Week3.pdf
```

## Domains & Their Categories

### Technology 🔧
- UAV, Web, Database, API, DevOps, AI, Cloud, Security, Mobile

### Finance 💰
- Accounting, Payroll, Maintenance, Budget, Investment, Expense, Tax

### Education 📚
- Programming, Mathematics, Science, Literature, History, Languages

### College 🎓
- Clubs, Courses, Events, Administration

### School 📖
- Assignments, Schedule, Events, Administration

### Company 🏢
- Product, Service, HR, Finance, Marketing

## How It Works

1. **Content Analysis** → Identifies domain keywords
2. **Category Detection** → Finds subcategory within domain
3. **File Recognition** → Extracts file extension
4. **Path Generation** → Creates `Domain/Category/FileType/`
5. **Auto Organization** → Files sorted automatically

## Adding New Domain

```python
# In core/llm.py

# 1. Add to DOMAIN_KEYWORDS
"Hospital": {
    "strong": ["patient", "medical", "treatment"],
    "weak": ["hospital", "clinic"]
}

# 2. Add to CATEGORY_KEYWORDS_BY_DOMAIN
"Hospital": {
    "Surgery": ["surgery", "surgical", "operating"],
    "Pediatrics": ["child", "infant", "pediatric"],
    "Other": []
}
```

## Key Files Modified
- `core/llm.py` - Classification logic
- `watcher.py` - File routing

## Test Files Location
```
data/incoming/  ← Drop files here for auto-processing
data/sorted/    ← Files automatically organized here
```

## Check Logs
```bash
# Watch watcher process files in real-time
python watcher.py
```

---

**Ready to scale! Add domains as needed.** 🚀
