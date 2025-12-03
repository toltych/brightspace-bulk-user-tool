
# ⚠️ Portfolio Project Notice

This repository contains sanitized code from a production automation project, presented as a portfolio piece.

## 🚀 Original Context
This tool resolved a critical incident in December 2024 by automating the correction of 1000+ course enrollments, reducing a 40+ hour manual process to ~2 hours.

## 🧼 Current State (Generalized)
The code has been sanitized for public sharing:
*   Institution-specific details (URLs, names) are removed.
*   XPath selectors are examples and must be updated.
*   Configuration values are placeholders.

## 🛑 Important: This Will NOT Work Out-of-the-Box

**DO NOT** expect to clone and run this code without significant modification.

### ✅ This repository serves as:
*   A demonstration of production automation capabilities.
*   A code sample of a problem-solving approach and technical skills.
*   A reference implementation to be adapted.

### ❌ This is NOT:
*   A ready-to-use tool for your Brightspace instance.

## 🛠️ What You'll Need to Modify
*   Update URLs in `selenium_uploader.py`.
*   Update XPath selectors in `Config.XPATHS`.
*   Verify CSV column names match your platform's requirements.
*   **Test thoroughly** in a non-production environment first.
*   Review your institution's policies on automation.

## 🧑‍💻 Intended Audience
*   Potential employers evaluating automation and development skills.
*   Systems administrators seeking reference implementations.
*   Developers interested in Selenium-based workflow automation.

## 📝 Disclaimer
By using this code, you acknowledge:
*   It requires significant customization.
*   You are responsible for testing and production use.
*   The author provides no warranty or support.
*   See the LICENSE file for full terms.

--------------------------------------------------------

# Brightspace Bulk User Management Automation

**Production automation tool for processing and uploading bulk enrollment data.**

## 🎯 Problem

During a production incident in December 2024, a role misconfiguration caused mass incorrect enrollments across 1000+ courses. Manual correction would have required 40+ hours of tedious, error-prone work clicking through web forms.

## 💡 Solution

Built a two-stage automation pipeline:

1. **CSV Generator**: Processes bulk enrollment data, validates for duplicates, and splits into manageable course-specific files
2. **Selenium Uploader**: Automates the multi-step web form submission process, eliminating manual clicking

## 📊 Impact

- **Time saved**: Reduced 40+ hour manual process to ~2 hours
- **Error elimination**: Automated validation prevented data entry mistakes
- **Reusability**: Tool used for subsequent bulk operations
- **Audit trail**: Comprehensive logging for compliance and debugging

## 🛠️ Tech Stack

- **Python 3.12+**
- **pandas** - Data processing and CSV manipulation
- **Selenium WebDriver** - Browser automation
- **Firefox/GeckoDriver** - Web browser control

## 📁 Project Structure

```
bulk-user-management/
├── csv_generator.py          # Splits bulk CSV into individual course files
├── selenium_uploader.py      # Automates file uploads via web interface
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── individual_courses/       # Output directory (created automatically)
└── batch_courses/            # Batch output directory (created automatically)
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bulk-user-management.git
cd bulk-user-management

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Step 1: Generate CSV Files

```bash
python csv_generator.py
```

**Input requirements:**
- CSV file with columns: `ACTION`, `USER_NAME`, `INSTRUCTOR_ID`, `COURSE_ID`
- No duplicate entries (script will warn if found)

**What it does:**
- Creates individual CSV file for each unique course
- Optionally groups files into batches by filter criteria (e.g., "2425_FA_BUS")
- Validates data integrity

**Example:**
```
Enter the path to your input CSV file: /path/to/enrollments.csv
Loaded 1500 records from input file.

Creating individual CSV files...
Created file: individual_courses/NM_2425_FA_BUS_101.csv
Created file: individual_courses/NM_2425_FA_BUS_102.csv
...
Created 247 individual CSV files in 'individual_courses' directory.

Do you want to group files into batches? (yes/no): yes
Enter your filter criteria: NM_2425_FA_BUS

Found 45 files matching 'NM_2425_FA_BUS'
Created batch file: batch_courses/NM_2425_FA_BUS_batch.csv
Total records in batch: 680
```

#### Step 2: Upload Files (Optional)

```bash
python selenium_uploader.py
```

**What it does:**
- Opens Firefox browser
- Navigates to platform URL (configure in `Config` class)
- Processes each CSV file:
  - Uploads file
  - Validates data
  - Unchecks email notifications
  - Imports data
  - Logs results

**Note**: Update the `Config.PLATFORM_URL` and `Config.XPATHS` in `selenium_uploader.py` to match your platform.

## ⚙️ Configuration

### Platform Settings (selenium_uploader.py)

```python
class Config:
    # Update this to your platform URL
    PLATFORM_URL = "https://your-platform.com/bulk-user-management"
    
    # Update XPath selectors to match your platform's HTML
    XPATHS = {
        'file_upload': "//input[@type='file']",
        'validate_button': "//button[contains(text(), 'Validate')]",
        # ... etc
    }
    
    # Adjust timeouts as needed
    DEFAULT_TIMEOUT = 300  # 5 minutes
```

### Finding XPath Selectors

1. Open your platform in Firefox
2. Right-click element → "Inspect"
3. Right-click in inspector → Copy → XPath
4. Update `Config.XPATHS` dictionary

## 📝 Features

### CSV Generator
- ✅ Input validation with duplicate detection
- ✅ Automatic directory creation
- ✅ Flexible batch filtering
- ✅ Progress logging
- ✅ Error handling

### Selenium Uploader
- ✅ Multi-step form automation
- ✅ Configurable timeouts
- ✅ Comprehensive logging
- ✅ Summary report generation
- ✅ Error recovery prompts
- ✅ Manual login support (security best practice)

## 🧪 Testing

Create sample test data:

```csv
ACTION,USER_NAME,INSTRUCTOR_ID,COURSE_ID
DROP,user1,INST001,TEST_2425_FA_CS_101
DROP,user2,INST002,TEST_2425_FA_CS_101
DROP,user3,INST003,TEST_2425_FA_CS_102
```

Run the CSV generator to verify output structure before using with production data.

## 📋 Example Workflow

**Scenario**: Need to drop 1000 users from 200 courses

```bash
# 1. Prepare input file with all enrollment changes
# Format: ACTION, USER_NAME, INSTRUCTOR_ID, COURSE_ID

# 2. Generate individual course files
python csv_generator.py
# Input: bulk_drops.csv (1000 records)
# Output: 200 individual CSV files

# 3. (Optional) Create batches for organized processing
# Filter by: "2425_SP" to get spring 2025 courses
# Output: batch_courses/2425_SP_batch.csv

# 4. (Optional) Automate uploads
python selenium_uploader.py
# Processes each file through web interface
# Generates detailed logs and summary report
```

## 🔍 Logging

Both scripts generate detailed logs:

- **CSV Generator**: Console output with file creation progress
- **Selenium Uploader**: 
  - Real-time console logging
  - Detailed log file: `upload_log_YYYYMMDD_HHMMSS.log`
  - Summary report: `upload_summary_YYYYMMDD_HHMMSS.log`

## 🚨 Production Notes

**This tool was built and tested in production during an incident response scenario.**

### Lessons Learned

**What Worked Well:**
- Selenium automation successfully handled complex multi-step workflow
- Logging provided crucial debugging information during execution
- Batch processing significantly reduced cognitive load
- Validation caught several potential issues before upload

**What I'd Do Differently:**
- Implement configurable timeouts instead of infinite waits
- Add comprehensive unit tests before production deployment
- Use configuration files instead of hardcoded values
- Implement retry logic for network failures
- Add progress bars for better UX during long operations

### Known Limitations

- **XPath Fragility**: Web interface changes will break selectors (requires updates)
- **Browser Dependency**: Requires Firefox and GeckoDriver
- **No Rollback**: Once imported, changes must be manually reversed
- **Single-threaded**: Processes files sequentially (could be parallelized)

### Future Improvements

- [ ] Replace XPath with more robust element identification (CSS selectors, IDs)
- [ ] Add unit tests for data processing logic
- [ ] Build web interface for non-technical users
- [ ] Implement async processing for large file batches
- [ ] Add database for tracking upload history
- [ ] Create generic framework adaptable to other LMS platforms
- [ ] Add Docker containerization for easy deployment
- [ ] Implement headless browser mode for server deployment

## 🤝 Contributing

This tool was created for a specific production use case but has been generalized for broader applicability. 

Contributions welcome:
- Platform-specific XPath configurations
- Error handling improvements
- Additional validation rules
- Performance optimizations

## 📄 License

MIT License - Feel free to adapt for your own use cases

## ⚠️ Disclaimer

This tool automates bulk operations that can affect many users simultaneously. Always:
- Test thoroughly with sample data first
- Verify XPath selectors match your platform
- Review validation results before importing
- Keep backups of original data
- Have a rollback plan ready

**Use at your own risk. The author assumes no liability for data loss or system issues.**

## 👤 Author -- (Toltych) - [Github](https://github.com/toltych)

Built by a systems administrator with 5 years of experience in IT operations, transitioning to DevOps/automation engineering.

**Skills demonstrated:**
- Production incident response
- Python automation and data processing
- Web scraping and browser automation
- Logging and monitoring
- Documentation and technical writing

---

**Note**: This project has been sanitized for public portfolio use. Original implementation was for a specific LMS platform during a production incident in December 2024.
