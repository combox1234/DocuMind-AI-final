# Hierarchical Classification System - Complete Upgrade

**Date:** December 16, 2025  
**Status:** ✅ **Production Ready**

---

## 🎯 Overview

The classification system has been scaled from **single-level categorization** to a powerful **three-tier hierarchical structure**:

```
Domain (Main Category)
├── Category (Subcategory)
│   └── FileType (File Extension)
```

**Example Paths:**
- `Technology/UAV/pptx/UAV_Technology_Unit3.pptx`
- `Finance/Maintenance/xlsx/Maintenance_2024.xlsx`
- `College/Clubs/pdf/CS_Club_Meeting.pdf`
- `Education/Programming/py/Python_OOP_Module3.py`
- `Company/Product/md/Product_Spec_v2.md`

---

## 📊 New Domain Structure

### 1. **Technology** 🔧
Sub-categories: UAV, Web, Database, API, DevOps, AI, Cloud, Security, Mobile
- **Files:** `UAV_Technology_Unit3.txt` → `Technology/UAV/txt/`
- **Best for:** Software projects, technical documentation, code-related content

### 2. **Finance** 💰
Sub-categories: Accounting, Payroll, Maintenance, Budget, Investment, Expense, Tax
- **Files:** `Maintenance_Expenses_2024.xlsx` → `Finance/Maintenance/xlsx/`
- **Best for:** Financial records, budgets, maintenance logs, expense reports

### 3. **Education** 📚
Sub-categories: Programming, Mathematics, Science, Literature, History, Languages
- **Files:** `Math_Assignment_Chapter5.pdf` → `Education/Mathematics/pdf/`
- **Best for:** Courses, assignments, learning materials, lectures, tutorials

### 4. **College** 🎓
Sub-categories: Clubs, Courses, Events, Administration
- **Files:** `CS_Club_Meeting.pdf` → `College/Clubs/pdf/`
- **Best for:** University-specific documents, student organizations, events

### 5. **School** 📖
Sub-categories: Assignments, Schedule, Events, Administration
- **Files:** `Math_Homework_Week3.pdf` → `School/Assignments/pdf/`
- **Best for:** K-12 education, grades, schedules, homework

### 6. **Company** 🏢
Sub-categories: Product, Service, HR, Finance, Marketing
- **Files:** `Product_Spec_MobileApp.md` → `Company/Product/md/`
- **Best for:** Business documents, product specs, service details

### Legacy Domains (Maintained for Compatibility)
- **Code:** BackendCode, FrontendCode, generic Code files
- **DataScience:** ML models, data analysis
- **Business:** Strategy, operations (superseded by Company domain)
- **Healthcare, Legal, ResearchPaper:** Medical, legal, academic content

---

## 🔄 Classification Process

### Step 1: Domain Detection
- Analyzes content keywords to identify the main domain
- Scores each domain based on keyword frequency and weight
- Bonus points for domain keywords in filename

**Example:**
```
Text: "UAV stands for Unmanned Aerial Vehicle..."
Keywords found: "uav" (+2), "drone" (+2), "flight" (+2) = 6 points for Technology
Result: Domain = "Technology"
```

### Step 2: Category Classification
- For the detected domain, identifies the specific subcategory
- Uses domain-specific keyword lists
- Filename hints provide extra weight

**Example:**
```
Domain: Technology
Text contains: "UAV", "quadcopter", "unmanned"
Categories in Technology: UAV, Web, Database, API...
Score: UAV keywords (3+) > Web (0) > Others
Result: Category = "UAV"
```

### Step 3: File Type Association
- Extracts file extension automatically
- Creates final three-tier path: `Domain/Category/FileType/`

**Example:**
```
File: "UAV_Technology_Unit3.pptx"
Extension: pptx
Result Path: Technology/UAV/pptx/
```

---

## 📋 Test Results - Validation

All test files classified correctly:

| File | Expected Path | Actual Path | Status |
|------|----------------|------------|--------|
| UAV_Technology_Unit3.txt | Technology/UAV/txt | Technology/UAV/txt | ✅ |
| Maintenance_Expenses_2024.txt | Finance/Maintenance/txt | Finance/Maintenance/txt | ✅ |
| CS_Club_Meeting.txt | College/Clubs/txt | College/Clubs/txt | ✅ |
| Math_Assignment_Chapter5.txt | Education/Mathematics/txt | Education/Mathematics/txt | ✅ |
| Product_Spec_MobileApp.txt | Company/Product/txt | Company/Product/txt | ✅ |
| Python_OOP_Module3.txt | Education/Programming/txt | Education/Programming/txt | ✅ |

---

## 🛠️ Code Changes

### `core/llm.py`
**New Class Attributes:**
- `DOMAIN_KEYWORDS`: Main domain keywords (Technology, Finance, Education, College, School, Company, etc.)
- `CATEGORY_KEYWORDS_BY_DOMAIN`: Domain-specific subcategories with keywords

**New Method:**
```python
def classify_hierarchical(self, text: str, filename: str = "") -> Dict[str, str]:
    """
    Returns: {
        "domain": "Technology",
        "category": "UAV",
        "file_extension": "pptx"
    }
    """
```

### `watcher.py`
**Updated File Processing Logic:**
```python
# New hierarchical classification
hierarchy = llm_service.classify_hierarchical(text, filepath.name)
domain = hierarchy["domain"]
category = hierarchy["category"]
file_ext = hierarchy["file_extension"]

# NEW PATH STRUCTURE: Domain/Category/FileType/
category_dir = SORTED_DIR / domain / category / file_ext
```

---

## 📁 Directory Structure Examples

### Before (Single-level)
```
sorted/
├── Code/
│   ├── Backend/
│   └── Frontend/
├── Education/
├── Business/
├── DataScience/
└── Documentation/
```

### After (Three-tier Hierarchical)
```
sorted/
├── Technology/
│   ├── UAV/
│   │   ├── pptx/
│   │   ├── txt/
│   │   └── docx/
│   ├── Web/
│   ├── Database/
│   └── ...
├── Finance/
│   ├── Maintenance/
│   │   ├── xlsx/
│   │   └── txt/
│   ├── Budget/
│   ├── Payroll/
│   └── ...
├── College/
│   ├── Clubs/
│   │   ├── pdf/
│   │   └── txt/
│   ├── Courses/
│   └── ...
├── Education/
│   ├── Programming/
│   ├── Mathematics/
│   └── ...
└── ...
```

---

## 🚀 Features & Benefits

### Scalability
- ✅ Easy to add new domains (e.g., Hospital, Government, Legal)
- ✅ Easy to add new subcategories within existing domains
- ✅ Support for multiple file types per category

### Organization
- ✅ Clear three-level hierarchy: Domain → Category → FileType
- ✅ Intuitive folder structure for users
- ✅ Eliminates flat, cluttered directories

### Flexibility
- ✅ Same category can exist across multiple domains if needed
- ✅ Files automatically sorted based on content analysis
- ✅ Fallback to "Other" for unclassifiable content

### Maintainability
- ✅ Centralized keyword definitions
- ✅ Easy to tune classification weights
- ✅ Clean separation of domain/category logic

---

## 📝 Adding New Domains

To add a new domain (e.g., "Hospital"):

### 1. Update `core/llm.py`

```python
DOMAIN_KEYWORDS = {
    # ... existing domains ...
    "Hospital": {
        "strong": ["patient", "medical", "treatment", "surgery", "diagnosis"],
        "weak": ["hospital", "clinic", "care"]
    }
}

CATEGORY_KEYWORDS_BY_DOMAIN = {
    # ... existing domains ...
    "Hospital": {
        "Surgery": ["surgery", "surgical", "operating room", "post-op"],
        "Pediatrics": ["child", "infant", "pediatric", "neonatal"],
        "Emergency": ["emergency", "trauma", "ambulance", "er"],
        "Other": []
    }
}
```

### 2. Test with Files
```
Create files in data/incoming/ and let watcher process them
```

### 3. Verify Structure
```
data/sorted/Hospital/Surgery/pdf/
data/sorted/Hospital/Pediatrics/docx/
data/sorted/Hospital/Emergency/pdf/
```

---

## 🔍 Keyword Tuning

### Adjust Domain Weights
```python
# core/llm.py - Increase importance of specific keywords
DOMAIN_KEYWORDS["Finance"]["strong"] = [
    # Add more finance-specific keywords
    "revenue", "profit", "cost", "budget"
]
```

### Adjust Category Weights
```python
# core/llm.py - Add subcategories to existing domain
CATEGORY_KEYWORDS_BY_DOMAIN["Company"]["NewCategory"] = [
    "keyword1", "keyword2", "keyword3"
]
```

---

## ⚠️ Important Notes

### Removed Legacy Structure
- ❌ Old `/Documentation` folder removed from `sorted/`
- ❌ Old flat `Category/Topic/Extension` replaced with `Domain/Category/FileType/`
- ✅ Code fully migrated to new system

### Backward Compatibility
- ✅ Database still works with legacy category names
- ✅ Old files remain in their locations (manual move optional)
- ✅ Web UI displays documents regardless of structure

### Best Practices
1. **Clear Filenames:** `UAV_Technology_Unit3.pptx` → Better classification
2. **Content Quality:** Rich text in files → More accurate classification
3. **Regular Tuning:** Monitor classifications and adjust keywords quarterly
4. **Testing:** Create diverse test files when adding new domains

---

## 📊 Classification Examples

### Example 1: UAV Presentation
```
File: Unit3_UAV.pptx
Content: "UAV stands for Unmanned Aerial Vehicle..."
Detection: 
  - Domain: Technology (UAV, drone, quadcopter keywords)
  - Category: UAV (uav-specific keywords)
  - Extension: pptx
Result: Technology/UAV/pptx/Unit3_UAV.pptx
```

### Example 2: Financial Maintenance Log
```
File: Maintenance_Log_Q4.xlsx
Content: "Item,Date,Cost,Maintenance,Repair..."
Detection:
  - Domain: Finance (cost, maintenance, budget keywords)
  - Category: Maintenance (maintenance-specific keywords)
  - Extension: xlsx
Result: Finance/Maintenance/xlsx/Maintenance_Log_Q4.xlsx
```

### Example 3: College Club Minutes
```
File: CS_Club_Minutes_Dec.pdf
Content: "Computer Science Club meeting..."
Detection:
  - Domain: College (club, organization, campus keywords)
  - Category: Clubs (club-specific keywords)
  - Extension: pdf
Result: College/Clubs/pdf/CS_Club_Minutes_Dec.pdf
```

---

## 🔧 Troubleshooting

### File Misclassified?
1. Check filename clarity (avoid generic names like "file.txt")
2. Verify content contains domain-specific keywords
3. Adjust keywords in `core/llm.py` CATEGORY_KEYWORDS or DOMAIN_KEYWORDS
4. Re-run watcher to reprocess

### Category Not Recognized?
1. Add category to `CATEGORY_KEYWORDS_BY_DOMAIN` for target domain
2. Define keywords for the category
3. Restart watcher service

### Extension Incorrect?
- Verify file has proper extension
- Check that file processing correctly extracts extension
- Manual rename can fix if necessary

---

## 📞 Support

**Questions?**
- Check [core/llm.py](core/llm.py) for keyword definitions
- Review [watcher.py](watcher.py) for classification logic
- Test files in `data/incoming/` and monitor `watcher` logs

---

## ✅ Verification Checklist

- [x] Hierarchical keywords defined in `core/llm.py`
- [x] `classify_hierarchical()` method implemented
- [x] `watcher.py` updated to use new classification
- [x] Path generation: `Domain/Category/FileType/`
- [x] Old `/Documentation` folder removed
- [x] Test files processed with correct classifications
- [x] All 6 test cases passing
- [x] New domains: Technology, Finance, College, School, Company
- [x] Backward compatibility maintained

---

**Status: ✅ READY FOR PRODUCTION**

The system is now ready to scale to handle complex document hierarchies with automatic intelligent classification across multiple domains and categories.
