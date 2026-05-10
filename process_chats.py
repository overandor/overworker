"""Process specific chat files through chat → repo → single file pipeline."""
import os
from chat_to_repo import ChatToRepoConverter
from repo_to_single_file import RepoToSingleFileConverter


def process_specific_chats():
    """Process the specific chat files mentioned by the user."""
    chat_directory = "/Users/jo/Downloads/docs/chatgpt-export-markdown"
    
    # Specific files to process
    target_files = [
        "ChatGPT-500$_Art_Selling_Tips.md",
        "ChatGPT-Abstract_Landscape_Description.pdf",
        "ChatGPT-Account_and_File_Inquiry.md",
        "ChatGPT-AI_Crisis_Triage_Prototype.md",
        "ChatGPT-AI_Crisis_Triage_System.md",
        "ChatGPT-AI_Trading_Code_Base_Sale_and_Workflow_Challenges.md",
        "ChatGPT-Appraisal_and_Benchmarking.md",
        "ChatGPT-Appraisal_and_System_Completion.md",
        "ChatGPT-Art_Critique_Chaos.md",
        "ChatGPT-Art_Critique_Commentary.md",
        "ChatGPT-Asset_Appraisal_in_Dollars.md",
        "ChatGPT-Assistant_response_analysis.md",
        "ChatGPT-Atomicity_and_Distance.md",
        "ChatGPT-Attention_as_Currency.md"
    ]
    
    # Initialize converters
    chat_converter = ChatToRepoConverter()
    repo_converter = RepoToSingleFileConverter()
    
    # Process each file
    all_repo_files = []
    
    for filename in target_files:
        filepath = os.path.join(chat_directory, filename)
        
        if not os.path.exists(filepath):
            print(f"Skipping {filename} - file not found")
            continue
        
        # Skip PDF files for now (need different handling)
        if filename.endswith('.pdf'):
            print(f"Skipping {filename} - PDF format not yet supported")
            continue
        
        try:
            print(f"Processing {filename}...")
            chat_file = chat_converter.parse_chat_file(filepath)
            repo_files = chat_converter.convert_chat_to_repo_structure(chat_file)
            all_repo_files.extend(repo_files)
            print(f"  ✓ Generated {len(repo_files)} repo files from {filename}")
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
    
    # Convert repo to single file
    if all_repo_files:
        print(f"\nConverting {len(all_repo_files)} repo files to single file...")
        combined_content = repo_converter.convert_repo_to_single_file(all_repo_files)
        
        # Write output
        output_path = "/Users/jo/Desktop/eee/overworker/combined_chat_repo.txt"
        repo_converter.write_combined_file(combined_content, output_path)
        print(f"✓ Combined file written to: {output_path}")
        print(f"  Total size: {len(combined_content)} characters")
    else:
        print("No files were processed successfully")


if __name__ == "__main__":
    process_specific_chats()
