"""
Selenium Automation for Bulk User Management File Uploads
Automates the process of uploading multiple CSV files through a web interface.
"""

import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Configuration
class Config:
    """Configuration settings for the uploader."""
    # Change to production URL when ready
    PLATFORM_URL = "https://test.example.com/bulk-user-management"
    
    # XPath locators - update these based on your platform
    XPATHS = {
        'file_upload': "//input[@id='ctl_7' and @type='file']",
        'email_checkbox': "//input[@id='z_f' and @type='checkbox']",
        'validate_button': "//button[@id='z_a' and contains(text(), 'Validate File')]",
        'see_results': "//button[@id='z_a' and contains(text(), 'See Validation Results')]",
        'continue_options': "//button[@id='z_a' and contains(text(), 'Continue to Options')]",
        'import_now': "//button[@id='z_a' and contains(text(), 'Import Now')]",
        'view_summary': "//button[@id='z_a' and contains(text(), 'View Summary')]",
        'done': "//button[@id='z_a' and contains(text(), 'Done')]",
    }
    
    # Timeouts (in seconds)
    DEFAULT_TIMEOUT = 300  # 5 minutes
    FILE_UPLOAD_TIMEOUT = 600  # 10 minutes for large files


# Set up logging
def setup_logging(script_dir):
    """Configure logging to file and console."""
    log_file = os.path.join(script_dir, f"upload_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def wait_for_element(driver, xpath, timeout=Config.DEFAULT_TIMEOUT):
    """
    Wait for an element to be present on the page.
    
    Args:
        driver: Selenium WebDriver instance
        xpath: XPath locator for the element
        timeout: Maximum time to wait in seconds
        
    Returns:
        WebElement if found, None if timeout
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except TimeoutException:
        logging.error(f"Timeout waiting for element: {xpath}")
        return None


def wait_and_click(driver, xpath, timeout=Config.DEFAULT_TIMEOUT):
    """
    Wait for an element to be clickable and click it.
    
    Args:
        driver: Selenium WebDriver instance
        xpath: XPath locator for the element
        timeout: Maximum time to wait in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        logging.info(f"Clicked element: {xpath}")
        return True
    except TimeoutException:
        logging.error(f"Timeout waiting to click: {xpath}")
        return False
    except Exception as e:
        logging.error(f"Error clicking element {xpath}: {e}")
        return False


def upload_file(driver, file_path):
    """
    Upload a single CSV file through the web interface.
    
    Args:
        driver: Selenium WebDriver instance
        file_path: Full path to the CSV file to upload
        
    Returns:
        bool: True if successful, False otherwise
    """
    filename = os.path.basename(file_path)
    logging.info(f"Starting upload for: {filename}")
    
    try:
        # Step 1: Upload file
        file_input = wait_for_element(driver, Config.XPATHS['file_upload'])
        if not file_input:
            return False
        
        file_input.send_keys(file_path)
        logging.info(f"File selected: {filename}")
        time.sleep(2)  # Give it a moment to register
        
        # Step 2: Click Validate File
        if not wait_and_click(driver, Config.XPATHS['validate_button']):
            return False
        
        # Step 3: See Validation Results
        if not wait_and_click(driver, Config.XPATHS['see_results']):
            return False
        
        # Step 4: Continue to Options
        if not wait_and_click(driver, Config.XPATHS['continue_options']):
            return False
        
        # Step 5: Uncheck email notification if present
        try:
            checkbox = driver.find_element(By.XPATH, Config.XPATHS['email_checkbox'])
            if checkbox.is_selected():
                checkbox.click()
                logging.info("Unchecked email notification")
        except NoSuchElementException:
            logging.info("No email checkbox found (may not be present)")
        
        # Step 6: Import Now
        if not wait_and_click(driver, Config.XPATHS['import_now'], timeout=Config.FILE_UPLOAD_TIMEOUT):
            return False
        
        # Step 7: View Summary
        if not wait_and_click(driver, Config.XPATHS['view_summary']):
            return False
        
        # Step 8: Click Done
        if not wait_and_click(driver, Config.XPATHS['done']):
            return False
        
        logging.info(f"Successfully completed upload for: {filename}")
        return True
        
    except Exception as e:
        logging.error(f"Error processing {filename}: {e}")
        return False


def write_summary_log(script_dir, file_statuses):
    """
    Write a summary log of all file upload attempts.
    
    Args:
        script_dir: Directory to save the summary log
        file_statuses: Dictionary mapping filenames to status strings
    """
    summary_path = os.path.join(script_dir, f"upload_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    with open(summary_path, "w") as f:
        f.write(f"Bulk Upload Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        success_count = sum(1 for status in file_statuses.values() if status == "SUCCESS")
        failure_count = len(file_statuses) - success_count
        
        f.write(f"Total files processed: {len(file_statuses)}\n")
        f.write(f"Successful uploads: {success_count}\n")
        f.write(f"Failed uploads: {failure_count}\n\n")
        f.write("=" * 60 + "\n\n")
        
        for filename, status in file_statuses.items():
            f.write(f"{filename}: {status}\n")
    
    logging.info(f"Summary log written to: {summary_path}")


def setup_driver():
    """
    Set up and configure the Selenium WebDriver.
    
    Returns:
        WebDriver instance
    """
    options = Options()
    options.add_argument("--start-maximized")
    
    # Uncomment to run headless (no browser window)
    # options.add_argument("--headless")
    
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    
    return driver


def main():
    """Main execution function."""
    script_dir = os.getcwd()
    logger = setup_logging(script_dir)
    
    print("=" * 60)
    print("Bulk User Management File Uploader")
    print("=" * 60)
    
    # Get CSV directory
    csv_directory = input("\nEnter the full path to the directory containing CSV files: ").strip()
    
    if not os.path.isdir(csv_directory):
        logger.error(f"Directory not found: {csv_directory}")
        return
    
    # Get list of CSV files
    csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]
    
    if not csv_files:
        logger.error(f"No CSV files found in: {csv_directory}")
        return
    
    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    # Confirm before proceeding
    print(f"\nFound {len(csv_files)} CSV files:")
    for f in csv_files[:5]:  # Show first 5
        print(f"  - {f}")
    if len(csv_files) > 5:
        print(f"  ... and {len(csv_files) - 5} more")
    
    proceed = input("\nProceed with upload? (yes/no): ").strip().lower()
    if proceed != "yes":
        logger.info("Upload cancelled by user")
        return
    
    # Set up Selenium
    logger.info("Initializing browser...")
    driver = setup_driver()
    file_statuses = {}
    
    try:
        # Navigate to platform
        driver.get(Config.PLATFORM_URL)
        logger.info(f"Navigated to: {Config.PLATFORM_URL}")
        
        # Wait for manual login
        input("\nPlease log in manually in the browser, then press Enter to continue...")
        
        # Process each CSV file
        for i, csv_file in enumerate(csv_files, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing file {i}/{len(csv_files)}: {csv_file}")
            logger.info(f"{'='*60}")
            
            file_path = os.path.join(csv_directory, csv_file)
            
            if upload_file(driver, file_path):
                file_statuses[csv_file] = "SUCCESS"
            else:
                file_statuses[csv_file] = "FAILED"
                
                # Ask if user wants to continue
                continue_upload = input(f"\nUpload failed for {csv_file}. Continue with remaining files? (yes/no): ").strip().lower()
                if continue_upload != "yes":
                    logger.info("Upload process stopped by user")
                    break
            
            # Small delay between files
            time.sleep(2)
        
    except KeyboardInterrupt:
        logger.warning("\nUpload process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Write summary and cleanup
        write_summary_log(script_dir, file_statuses)
        
        input("\nPress Enter to close the browser...")
        driver.quit()
        
        logger.info("\nUpload process complete")


if __name__ == "__main__":
    main()
