"""Workspace manager for organizing video projects"""
import os
import time
from datetime import datetime

# Root folder for all video projects
WORKSPACE_ROOT = "ChitraAI_Projects"

def create_unique_project_folder(project_type="video"):
    """
    Create a unique project folder with timestamp-based ID.
    
    Args:
        project_type: Type of project (e.g., 'reels', 'long_video', 'topic_to_reels')
    
    Returns:
        tuple: (project_folder_path, project_id)
    """
    # Create root workspace if it doesn't exist
    if not os.path.exists(WORKSPACE_ROOT):
        os.makedirs(WORKSPACE_ROOT)
        print(f"✓ Created workspace: {WORKSPACE_ROOT}/")
    
    # Generate unique ID: timestamp + type
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_id = f"{project_type}_{timestamp}"
    
    # Create project folder
    project_folder = os.path.join(WORKSPACE_ROOT, project_id)
    os.makedirs(project_folder, exist_ok=True)
    
    # Create assets subfolder
    assets_folder = os.path.join(project_folder, "assets")
    os.makedirs(assets_folder, exist_ok=True)
    
    # Create temp subfolder
    temp_folder = os.path.join(project_folder, "temp")
    os.makedirs(temp_folder, exist_ok=True)
    
    print(f"✓ Created project: {project_id}/")
    print(f"  └─ assets/")
    print(f"  └─ temp/")
    
    return project_folder, project_id


def get_project_paths(project_folder):
    """
    Get all standard paths for a project.
    
    Args:
        project_folder: Path to the project folder
    
    Returns:
        dict: Dictionary with all project paths
    """
    return {
        'root': project_folder,
        'assets': os.path.join(project_folder, 'assets'),
        'temp': os.path.join(project_folder, 'temp'),
        'audio': os.path.join(project_folder, 'audio.mp3'),
        'video_map': os.path.join(project_folder, 'video_map.json'),
        'script': os.path.join(project_folder, 'generated_script.json'),
        'clean_script': os.path.join(project_folder, 'clean_script.txt'),
        'captions': os.path.join(project_folder, 'captions.ass'),
        'draft_video': os.path.join(project_folder, 'draft_video.mp4'),
        'final_output': os.path.join(project_folder, 'final_output.mp4'),
        'logo': os.path.join(project_folder, 'logo.png'),
        'metadata': os.path.join(project_folder, 'metadata.json')
    }


def cleanup_project_temp(project_folder):
    """Clean up temporary files in project folder."""
    temp_folder = os.path.join(project_folder, 'temp')
    if os.path.exists(temp_folder):
        for file in os.listdir(temp_folder):
            try:
                os.remove(os.path.join(temp_folder, file))
            except:
                pass


def list_projects():
    """List all projects in workspace."""
    if not os.path.exists(WORKSPACE_ROOT):
        return []
    
    projects = []
    for folder in os.listdir(WORKSPACE_ROOT):
        folder_path = os.path.join(WORKSPACE_ROOT, folder)
        if os.path.isdir(folder_path):
            projects.append({
                'id': folder,
                'path': folder_path,
                'created': os.path.getctime(folder_path)
            })
    
    # Sort by creation time (newest first)
    projects.sort(key=lambda x: x['created'], reverse=True)
    return projects


if __name__ == '__main__':
    # Test the workspace manager
    print("=== ChitraAI Workspace Manager ===\n")
    
    # Create a test project
    project_folder, project_id = create_unique_project_folder("test")
    print(f"\nProject ID: {project_id}")
    print(f"Project Path: {project_folder}")
    
    # Get paths
    paths = get_project_paths(project_folder)
    print("\nProject Paths:")
    for key, path in paths.items():
        print(f"  {key}: {path}")
    
    # List all projects
    print("\nAll Projects:")
    projects = list_projects()
    for p in projects:
        print(f"  - {p['id']}")
