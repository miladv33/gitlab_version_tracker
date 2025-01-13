import gitlab
import datetime
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitLab configuration from environment variables
GITLAB_URL = os.getenv('GITLAB_URL', 'https://gitlab.com/')
PRIVATE_TOKEN = os.getenv('GITLAB_PRIVATE_TOKEN')
PROJECT_ID = os.getenv('GITLAB_PROJECT_ID')
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL', 'https://nexttoptech.atlassian.net/browse/')

# Project-specific configuration
TARGET_BRANCH = os.getenv('TARGET_BRANCH', 'test')
VERSION_PATTERN = os.getenv('VERSION_PATTERN', r'\[TCPRJ-UPDATE-VERSION\]-to VN-(\d+)')
VERSION_NUMBER_GROUP = int(os.getenv('VERSION_NUMBER_GROUP', '1'))  # Which regex group contains the version number
TICKET_PATTERN = os.getenv('TICKET_PATTERN', r'\[([A-Z]+-\d+)\](.+)')  # Pattern for JIRA ticket detection
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '.')  # Directory for output files

# Validate required environment variables
if not all([PRIVATE_TOKEN, PROJECT_ID]):
    raise ValueError(
        "Missing required environment variables. Please ensure GITLAB_PRIVATE_TOKEN "
        "and GITLAB_PROJECT_ID are set in your .env file."
    )

# Initialize GitLab client
gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)
project = gl.projects.get(PROJECT_ID)


def find_version_boundaries():
    """
    Find the version update merge requests we want to look between.
    Returns tuple of (previous_version_mr, current_version_mr).
    """
    # Get all merged merge requests in reverse chronological order (newest first)
    all_mrs = project.mergerequests.list(
        state='merged',
        order_by='created_at',
        sort='desc',
        all=True  # Make sure we get all MRs, not just the first page
    )

    version_pattern = re.compile(VERSION_PATTERN)
    version_dict = {}  # Keep track of unique version numbers and their first occurrence

    # Collect version update merge requests, keeping only the first occurrence of each version
    for mr in all_mrs:
        match = version_pattern.match(mr.title)
        if match:
            version_number = int(match.group(VERSION_NUMBER_GROUP))
            # Only keep the first (most recent) occurrence of each version
            if version_number not in version_dict:
                version_dict[version_number] = mr

    # Convert to list and sort by version number
    version_mrs = [(version, mr) for version, mr in version_dict.items()]
    version_mrs.sort(key=lambda x: x[0], reverse=True)

    if len(version_mrs) < 2:
        return None, None

    # Get the latest version and the one before it
    current_version = version_mrs[0][1]  # Highest version number
    previous_version = version_mrs[1][1]  # Second highest version number

    print(f"Found versions:")
    print(f"Current: VN-{version_mrs[0][0]}")
    print(f"Previous: VN-{version_mrs[1][0]}")

    return previous_version, current_version


def get_merge_requests_between_versions(start_mr, end_mr):
    """Get all merge requests between two version update merge requests."""
    # Get all merge requests between the two dates
    all_mrs = project.mergerequests.list(
        state='merged',
        created_after=start_mr.created_at,
        created_before=end_mr.created_at,
        order_by='created_at',
        sort='asc',
        all=True  # Make sure we get all MRs, not just the first page
    )

    # Filter for:
    # 1. Target branch is 'test'
    # 2. Exclude the start version MR but include the end version MR
    filtered_mrs = [
        mr for mr in all_mrs
        if mr.target_branch == TARGET_BRANCH and mr.iid != start_mr.iid
    ]

    # Sort by creation date in reverse order (newest first)
    filtered_mrs.sort(key=lambda x: x.created_at, reverse=True)
    return filtered_mrs


def get_commits_for_mr(mr):
    """Get commits for a merge request."""
    commits = mr.commits()
    return commits


def sanitize_text(text):
    """Sanitize text to handle potential encoding issues."""
    if text is None:
        return ""
    try:
        # Try to encode and decode to catch any encoding issues
        return text.encode('utf-8', errors='replace').decode('utf-8')
    except Exception:
        return ""


def write_changes_to_file(merge_requests, start_version, end_version, filename):
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    def format_title(title):
        match = re.match(TICKET_PATTERN, title)
        if match and JIRA_BASE_URL:
            ticket_id = match.group(1)
            rest_of_title = match.group(2)
            return f'# [{ticket_id}]({JIRA_BASE_URL}{ticket_id}){rest_of_title}\n\n'
        return f'# {title}\n\n'

    def format_message(message):
        match = re.match(TICKET_PATTERN, message)
        if match and JIRA_BASE_URL:
            ticket_id = match.group(1)
            rest_of_message = match.group(2)
            return f'[{ticket_id}]({JIRA_BASE_URL}{ticket_id}){rest_of_message}'
        return message

    with open(filename, 'w', encoding='utf-8') as f:
        # Write header with version information
        f.write(f"# Changes between versions\n\n")
        f.write(f"From: {start_version.title}\n")
        f.write(f"To: {end_version.title}\n\n")
        f.write("---\n\n")

        for mr in merge_requests:
            f.write(format_title(mr.title))
            f.write(f"Merge Request: !{mr.iid}\n\n")

            commits = get_commits_for_mr(mr)
            for commit in commits:
                f.write(f"## Commit: {commit.short_id}\n\n")
                f.write(f"**Author:** {commit.author_name}\n\n")
                f.write(f"**Message:** {format_message(commit.message)}\n\n")

                try:
                    diff = commit.diff()
                    for change in diff:
                        f.write(f"### File: {sanitize_text(change['new_path'])}\n\n")
                        f.write("```diff\n")
                        f.write(sanitize_text(change['diff']))
                        f.write("\n```\n\n")
                except Exception as e:
                    print(f"Warning: Could not process diff for commit {commit.short_id}: {e}")

            f.write("---\n\n")


def generate_file_name():
    now = datetime.datetime.now()
    base_name = f"merge_request_changes_{now.strftime('%Y-%m-%d_%H-%M-%S')}.md"
    return os.path.join(OUTPUT_DIR, base_name)


def main():
    # Find the version boundaries
    previous_version, current_version = find_version_boundaries()

    if not previous_version or not current_version:
        print("Could not find enough version update merge requests.")
        return

    print(f"Finding merge requests between:")
    print(f"Previous version: {previous_version.title} (Created: {previous_version.created_at})")
    print(f"Current version: {current_version.title} (Created: {current_version.created_at})")

    # Get merge requests between these versions
    merge_requests = get_merge_requests_between_versions(previous_version, current_version)

    output_file = generate_file_name()
    write_changes_to_file(merge_requests, previous_version, current_version, output_file)

    print(f"\nFound {len(merge_requests)} merge requests to 'test' branch")
    print(f"Changes have been written to {output_file}")


if __name__ == "__main__":
    main()