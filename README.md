# GitLab Version Change Tracker

## Overview

The GitLab Version Change Tracker is a Python script designed to generate comprehensive change reports between different versions of your project in GitLab. It automatically identifies version-related merge requests, collects all changes between versions, and generates a detailed Markdown report including commit information, diffs, and (optionally) JIRA ticket references.

## Features

- Automatically detects version boundaries based on merge request patterns
- Filters merge requests by target branch
- Generates detailed change reports in Markdown format
- Includes commit messages, authors, and file diffs
- Optional JIRA ticket integration with clickable links
- Highly configurable through environment variables
- Handles UTF-8 encoding and text sanitization
- Supports custom version numbering patterns
- Configurable output location for generated reports

## Prerequisites

### System Requirements

- Python 3.x
- Git
- Access to a GitLab repository
- GitLab personal access token with appropriate permissions

### Required Python Packages

```bash
pip install python-gitlab
pip install python-dotenv
```

### GitLab Requirements

1. Personal Access Token with the following permissions:
   - api
   - read_repository
   - read_api

2. Project ID (found in your GitLab project's main page)
3. Access rights to view merge requests and commits

## Installation

1. Clone or download the script to your local machine
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the script directory
4. Add `.env` to your `.gitignore`:
   ```bash
   echo ".env" >> .gitignore
   ```

## Configuration

### Essential Environment Variables

Create a `.env` file with the following configurations:

```bash
# Required Configuration
GITLAB_PRIVATE_TOKEN=your_token_here
GITLAB_PROJECT_ID=your_project_id

# Optional Configuration with Defaults
GITLAB_URL=https://gitlab.com/
JIRA_BASE_URL=https://your-jira-instance.atlassian.net/browse/
TARGET_BRANCH=test
VERSION_PATTERN=\[TCPRJ-UPDATE-VERSION\]-to VN-(\d+)
VERSION_NUMBER_GROUP=1
TICKET_PATTERN=\[([A-Z]+-\d+)\](.+)
OUTPUT_DIR=.
```

### Configuration Options Explained

#### Required Settings

- `GITLAB_PRIVATE_TOKEN`: Your GitLab personal access token
- `GITLAB_PROJECT_ID`: Your GitLab project ID

#### Optional Settings

- `GITLAB_URL`: Base URL of your GitLab instance (default: https://gitlab.com/)
- `JIRA_BASE_URL`: Base URL of your JIRA instance (leave empty to disable JIRA integration)
- `TARGET_BRANCH`: Branch to track for merge requests (default: test)
- `VERSION_PATTERN`: Regex pattern for identifying version update merge requests
- `VERSION_NUMBER_GROUP`: Which regex group contains the version number (default: 1)
- `TICKET_PATTERN`: Regex pattern for identifying ticket references
- `OUTPUT_DIR`: Directory where reports will be saved (default: current directory)

## Usage

### Basic Usage

Run the script from the command line:

```bash
python gitlab_version_tracker.py
```

### Example Configurations for Different Projects

1. Standard Version Numbers:
```bash
VERSION_PATTERN=release-v(\d+\.\d+\.\d+)
TARGET_BRANCH=main
```

2. Different Ticket Format:
```bash
TICKET_PATTERN=\((PROJ-\d+)\)(.+)
```

3. Custom Output Location:
```bash
OUTPUT_DIR=/path/to/reports
```

### Output Format

The script generates a Markdown file with the following structure:

```markdown
# Changes between versions

From: [Previous Version Title]
To: [Current Version Title]

---

# [Ticket-ID] Merge Request Title

Merge Request: !123

## Commit: abc123

**Author:** John Doe

**Message:** [Ticket-ID] Commit message

### File: path/to/changed/file

```diff
+ Added line
- Removed line
```

---
```

## Best Practices

### Security

1. Never commit your `.env` file
2. Rotate your GitLab token periodically
3. Use minimal required permissions for the token
4. Keep your Python packages updated

### Performance

1. Test with small date ranges first
2. Consider implementing rate limiting for large repositories
3. Monitor script execution time and memory usage
4. Use appropriate error handling for network issues

### Version Control

1. Maintain consistent version numbering in merge requests
2. Follow a consistent merge request naming convention
3. Properly merge (don't close) version-related merge requests
4. Keep commit messages clear and consistent

### JIRA Integration

1. Use consistent ticket reference formatting
2. Verify JIRA URL accessibility
3. Include ticket references in both merge request titles and commit messages
4. Test JIRA link generation before large runs

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Errors**
   - Verify token permissions
   - Check token expiration
   - Ensure correct GitLab URL

2. **Pattern Matching Issues**
   - Verify version pattern matches your conventions
   - Check regex groups in patterns
   - Test patterns with sample data

3. **Missing Data**
   - Verify merge request state (should be merged)
   - Check target branch configuration
   - Verify access permissions

4. **Encoding Problems**
   - Check file encoding (should be UTF-8)
   - Verify text sanitization
   - Check for special characters in commits

## Advanced Usage

### Custom Pattern Examples

1. Semantic Versioning:
```bash
VERSION_PATTERN=v(\d+\.\d+\.\d+)
```

2. Build Numbers:
```bash
VERSION_PATTERN=build-(\d+)
```

3. Date-based Versions:
```bash
VERSION_PATTERN=release-(\d{8})
```

### Output Customization

The script supports customization of the output format through code modifications. Key areas for customization:

1. Markdown formatting
2. Diff presentation
3. Commit information display
4. Report organization

## Contributing

When contributing to this project:

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style
4. Add appropriate tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- GitLab API documentation
- Python-GitLab library
- Python-dotenv project

## Support

For issues and questions:

1. Check the troubleshooting guide
2. Review GitLab API documentation
3. Check Python-GitLab documentation
4. Submit an issue with detailed information

