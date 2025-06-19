# InfoHarvest
A simple contact info scraping tool written in Python and available as an executable file. It has a CLI & a GUI. This scripts main function is also integrated into [ClatScope Info Tool](Github.com/Clatcope).

# Website Contact Info Scraper

#![Screenshot 2025-06-19 141011](https://github.com/user-attachments/assets/107bad4d-a1c0-4da4-a818-419d31d71c28)

# Overview

This Python script is a comprehensive tool designed to extract and display contact information from websites. It retrieves phone numbers, fax numbers, email addresses, and social media profile URLs directly from a given website's HTML content.

## Purpose

The primary use of this script is for Open Source Intelligence (OSINT), digital marketing, customer relations management, competitive analysis, or investigative tasks that require identification and cataloguing of contact details from various online sources.

## Key Features

* **Automatic Dependency Installation**: Automatically checks and installs required Python libraries (`requests`, `BeautifulSoup`).
* **Detailed Information Extraction**: Precisely extracts phone numbers, fax numbers, emails, and social media URLs.
* **Regular Expression-Based Parsing**: Uses robust regex patterns to reliably identify contact information.
* **Contextual Identification**: Differentiates between phone and fax numbers by context within the webpage.
* **Duplicate and Spam Reduction**: Filters redundant or repetitive contact information.

## Usage

### Requirements

* Python 3.x installed on your system.

### Installation

1. Save the script file to your local machine.
2. Ensure Python is installed and available via the command line.

### Execution

Run the script from a command line or terminal

### Interaction

* Upon execution, the script prompts the user for a full URL.
* Enter the complete URL (e.g., `https://example.com`) to scrape contact details.
* Pressing `Enter` without entering a URL will terminate the script gracefully.

### Output

The extracted contact information is clearly formatted as JSON:

```json
{
  "Phone numbers": "555-123-4567, 555-765-4321",
  "Fax number": "555-111-2222",
  "Email addresses": "info@example.com, contact@example.org",
  "Social media profiles": "https://twitter.com/example, https://linkedin.com/company/example"
}
```

### Error Handling

The script includes basic error handling and provides feedback if the URL is invalid or inaccessible.

## Limitations

* Relies on publicly visible HTML content; will not extract data hidden behind JavaScript-heavy pages or authenticated portals.
* Sensitive to changes in website HTML structures.

## License

This project is licensed under the Apache 2.0 open source license. 

## Author

Joshua M Clatney (Clats97)

Ethical Pentesting Enthusiast

Copyright © 2024-2025 Joshua M Clatney (Clats97) All Rights Reserved

**DISCLAIMER: This project comes with no warranty, express or implied. The author is not responsible for abuse, misuse, or vulnerabilities. Please use responsibly and ethically in accordance with relevant laws, regulations, legislation and best practices.**
