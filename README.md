# Automated Keyword-to-Product Assortment Validator

> A QA automation tool that uses Python and Selenium to validate the relevance of search results by ensuring product attributes match the searched keywords, significantly reducing manual testing time.

## 1. The Business Problem
Within our DLP (Data & Listing Quality) testing workflow, the manual QA team was spending a significant amount of time on a repetitive but critical task: verifying keyword-assortment quality. For a given keyword (e.g., "men's blue running shoes"), they had to manually search the e-commerce site and then individually check each resulting product to ensure its attributes (the "payload") correctly matched the keywords. This process was:

-   **Extremely Time-Consuming:** A single keyword could require checking 10-20 product pages.
-   **Prone to Human Error:** It's easy to miss a mismatched attribute when checking hundreds of items.
-   **Not Scalable:** It was impossible to achieve comprehensive test coverage across the thousands of important keywords.

## 2. My Solution
I developed a Python-based automation framework to completely take over this validation task. The tool directly mimics and enhances the manual QA process, providing faster, more accurate, and more comprehensive results.

Here is the automated workflow:

1.  **Keyword Input:** The script takes a list of keywords from a simple file (e.g., a CSV).
2.  **Browser Automation:** For each keyword, it launches a Selenium-controlled browser instance, navigates to the website, and executes a search.
3.  **Product Scraping:** It intelligently scrapes the key data from each product listed on the search results page.
4.  **Attribute Validation Logic:** The core of the tool is its validation engine. It tokenizes the search keyword (e.g., `["men's", "blue", "running", "shoes"]`) and cross-references these tokens against the scraped data for each product.
5.  **Detailed Reporting:** The script generates a clear, concise report that flags every keyword where one or more products failed the validation check, pinpointing the exact discrepancies.

This solution provides a deterministic and objective answer to the question: "Are the products shown for this keyword relevant?"

## 3. Technologies & Skills
-   **Language:** Python
-   **Core Libraries:** Selenium (for browser automation), Pandas (for data handling and reporting)
-   **Skills:**
    -   QA Automation & Test Strategy
    -   Web Scraping & Browser Automation
    -   Data Validation & Business Logic Implementation
    -   Process Improvement & Workflow Optimization

## 4. Key Features
-   **Keyword-Driven Framework:** The entire testing process is driven by an easily editable list of keywords, requiring no code changes to expand test coverage.
-   **Smart Validation:** The script doesn't just check for the whole string; it validates the presence of individual, critical attribute tokens from the keyword.
-   **Scalability:** Can process hundreds of keywords in the time it takes a manual tester to complete just a few.
-   **Actionable Reports:** The output clearly indicates which keywords need review, allowing the QA team to focus their efforts where they are most needed.

## 5. The Impact
This tool was a game-changer for the DLP quality testing workflow.
-   **Massive Time Savings:** Reduced the manual QA time spent on keyword validation by over **95%**.
-   **Increased Test Coverage:** Allowed the team to expand from testing a few dozen keywords to testing hundreds, drastically improving the quality of site search results.
-   **Eliminated Human Error:** Provided consistent and reliable validation, leading to higher confidence in the quality of our product assortments.

## 6. How to Use
1.  `git clone https://github.com/shhhetty/assortment_validator.git`
2.  `cd assortment_validator`
3.  `pip install -r requirements.txt`
4.  Ensure you have the correct WebDriver installed and configured for your browser (e.g., chromedriver).
5.  Create a `keywords.csv` file in the root directory with a single column named "keyword".
6.  `python validator_script.name.py` (update with your script's name)
7.  Check the generated `validation_report.csv` for the results.
