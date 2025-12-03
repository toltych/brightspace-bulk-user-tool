"""
CSV Generator for Bulk User Management
Processes bulk enrollment data and creates individual CSV files per course.
Optionally groups files into batches based on filter criteria.
"""

import pandas as pd
import os
import glob


def create_output_directories():
    """Create output directories for individual and batch files."""
    output_dir = "individual_courses"
    batch_dir = "batch_courses"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(batch_dir, exist_ok=True)
    return output_dir, batch_dir


def validate_input_data(data):
    """
    Validate input CSV data for required columns and duplicates.
    
    Args:
        data: pandas DataFrame containing the input data
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    required_columns = ['ACTION', 'USER_NAME', 'INSTRUCTOR_ID', 'COURSE_ID']
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        return False
    
    # Check for duplicates (excluding ACTION column)
    check_columns = ['USER_NAME', 'INSTRUCTOR_ID', 'COURSE_ID']
    duplicates = data[check_columns].duplicated()
    
    if duplicates.any():
        print("\nWarning: Duplicate entries found in input file:")
        print(data[duplicates][check_columns])
        print("\nThese will be duplicated in output files.")
        
        proceed = input("\nDo you want to continue anyway? (yes/no): ").strip().lower()
        if proceed != "yes":
            return False
    
    return True


def create_individual_csv_files(data, output_dir):
    """
    Create individual CSV files for each unique COURSE_ID.
    
    Args:
        data: pandas DataFrame containing the enrollment data
        output_dir: Directory to save individual CSV files
        
    Returns:
        list: List of unique course IDs processed
    """
    # Extract columns
    action = data['ACTION']
    user_name = data['USER_NAME']
    instructor_id = data['INSTRUCTOR_ID']
    course_id = data['COURSE_ID']
    
    # Get unique COURSE_IDs
    unique_course_ids = course_id.unique()
    
    # Create individual CSV files for each COURSE_ID
    for unique_id in unique_course_ids:
        # Create a new dataframe for this course_id
        course_data = pd.DataFrame({
            'ACTION': action,
            'USER_NAME': user_name,
            'INSTRUCTOR_ID': instructor_id,
            'COURSE_ID': unique_id
        })
        
        # Save to CSV
        output_file = os.path.join(output_dir, f"{unique_id}.csv")
        course_data.to_csv(output_file, index=False)
        print(f"Created file: {output_file}")
    
    return unique_course_ids


def create_batch_files(output_dir, batch_dir, filter_criteria):
    """
    Group individual CSV files into batches based on filter criteria.
    
    Args:
        output_dir: Directory containing individual CSV files
        batch_dir: Directory to save batch CSV files
        filter_criteria: String to filter filenames by
    """
    # Find all CSV files matching the filter criteria
    all_files = glob.glob(os.path.join(output_dir, "*.csv"))
    filtered_files = [f for f in all_files if filter_criteria in os.path.basename(f)]
    
    if not filtered_files:
        print(f"\nNo files found matching criteria: '{filter_criteria}'")
        return
    
    print(f"\nFound {len(filtered_files)} files matching '{filter_criteria}':")
    for f in filtered_files:
        print(f"  - {os.path.basename(f)}")
    
    # Concatenate all matching files
    batch_data = pd.concat([pd.read_csv(f) for f in filtered_files], ignore_index=True)
    
    # Save batch file
    batch_filename = f"{filter_criteria}_batch.csv"
    batch_path = os.path.join(batch_dir, batch_filename)
    batch_data.to_csv(batch_path, index=False)
    
    print(f"\nCreated batch file: {batch_path}")
    print(f"Total records in batch: {len(batch_data)}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("CSV Generator for Bulk User Management")
    print("=" * 60)
    
    # Get input file
    input_file = input("\nEnter the path to your input CSV file: ").strip()
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return
    
    # Read the input CSV file
    try:
        data = pd.read_csv(input_file)
        print(f"\nLoaded {len(data)} records from input file.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Validate input data
    if not validate_input_data(data):
        print("\nValidation failed. Exiting.")
        return
    
    # Create output directories
    output_dir, batch_dir = create_output_directories()
    
    # Create individual CSV files
    print("\nCreating individual CSV files...")
    unique_course_ids = create_individual_csv_files(data, output_dir)
    print(f"\nCreated {len(unique_course_ids)} individual CSV files in '{output_dir}' directory.")
    
    # Ask about batch grouping
    group_files = input("\nDo you want to group files into batches? (yes/no): ").strip().lower()
    
    if group_files == "yes":
        print("\n" + "=" * 60)
        print("Batch Grouping Options")
        print("=" * 60)
        print("\nYou can filter files by:")
        print("  - College code (e.g., NM, KV)")
        print("  - Academic year (e.g., 2324, 2425)")
        print("  - Term (e.g., FA, SP, SU)")
        print("  - Course code (e.g., BUS, COE, NUT)")
        print("  - Course type (e.g., CO, CS)")
        print("\nYou can combine filters: 'NM_2425_FA_BUS' or '2425_SP'")
        
        while True:
            filter_criteria = input("\nEnter your filter criteria (or 'done' to finish): ").strip()
            
            if filter_criteria.lower() == 'done':
                break
            
            create_batch_files(output_dir, batch_dir, filter_criteria)
            
            another = input("\nCreate another batch? (yes/no): ").strip().lower()
            if another != "yes":
                break
    
    print("\n" + "=" * 60)
    print("Process complete!")
    print("=" * 60)
    print(f"\nIndividual files: ./{output_dir}/")
    print(f"Batch files: ./{batch_dir}/")


if __name__ == "__main__":
    main()
