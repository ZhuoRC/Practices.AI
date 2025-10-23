/**
 * Canada Immigration Processing Times Scraper using Chrome DevTools MCP
 *
 * This script demonstrates how to automate the retrieval of processing times
 * from the Canadian Immigration website using the Chrome DevTools MCP protocol.
 *
 * The form workflow is:
 * 1. Select application category from first dropdown
 * 2. Select specific application type from second dropdown (appears after step 1)
 * 3. Select country from third dropdown (appears after step 2)
 * 4. Click "Get processing time" button
 * 5. Extract the processing time from the results
 */

const CANADA_PROCESSING_TIMES_URL =
  "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html";

/**
 * Application categories available
 */
const CATEGORIES = {
  TEMPORARY_RESIDENCE: "Temporary residence (visiting, studying, working)",
  ECONOMIC_IMMIGRATION: "Economic immigration",
  FAMILY_SPONSORSHIP: "Family sponsorship",
  REFUGEES: "Refugees",
  HUMANITARIAN: "Humanitarian and compassionate cases",
  PASSPORT: "Passport",
  CITIZENSHIP: "Citizenship",
  PR_CARD: "Permanent resident cards",
  DOCUMENTS: "Replacing or amending documents, verifying status"
};

/**
 * Temporary residence application types
 */
const TEMP_RESIDENCE_TYPES = {
  VISITOR_VISA_OUTSIDE: "Visitor visa (from outside Canada)",
  VISITOR_VISA_INSIDE: "Visitor visa (from inside Canada)",
  VISITOR_EXTENSION: "Visitor extension (Visitor record)",
  SUPER_VISA: "Super visa (parents or grandparents)",
  STUDY_PERMIT_OUTSIDE: "Study permit (from outside Canada)",
  STUDY_PERMIT_INSIDE: "Study permit (from inside Canada)",
  STUDY_PERMIT_EXTENSION: "Study permit extension",
  WORK_PERMIT_OUTSIDE: "Work permit (from outside Canada)",
  WORK_PERMIT_INSIDE: "Work permit from inside Canada (initial and extension)",
  SAWP: "Seasonal Agricultural Worker Program (SAWP)",
  IEC: "International Experience Canada (IEC)",
  ETA: "Electronic Travel Authorization (eTA)"
};

/**
 * Helper function to wait for an element to appear
 */
async function waitForElement(selector, timeout = 5000) {
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    const element = document.querySelector(selector);
    if (element) return element;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error(`Element ${selector} not found after ${timeout}ms`);
}

/**
 * Helper function to select a dropdown option
 */
function selectDropdownOption(selectElement, optionText) {
  const options = Array.from(selectElement.options);
  const option = options.find(opt => opt.text === optionText);

  if (!option) {
    throw new Error(`Option "${optionText}" not found`);
  }

  selectElement.value = option.value;
  selectElement.dispatchEvent(new Event('change', { bubbles: true }));
  selectElement.dispatchEvent(new Event('input', { bubbles: true }));

  return true;
}

/**
 * Get processing time for a specific application
 */
async function getProcessingTime(category, applicationType, country) {
  try {
    // Step 1: Select application category
    const categorySelect = document.querySelectorAll('select')[0];
    if (!categorySelect) {
      throw new Error('Category select not found');
    }

    selectDropdownOption(categorySelect, category);
    console.log(`Selected category: ${category}`);

    // Wait for second dropdown to appear
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Step 2: Select application type
    const typeSelects = document.querySelectorAll('select');
    const typeSelect = typeSelects[1];
    if (!typeSelect) {
      throw new Error('Application type select not found');
    }

    selectDropdownOption(typeSelect, applicationType);
    console.log(`Selected application type: ${applicationType}`);

    // Wait for third dropdown to appear
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Step 3: Select country
    const countrySelects = document.querySelectorAll('select');
    const countrySelect = countrySelects[2];
    if (!countrySelect) {
      throw new Error('Country select not found');
    }

    selectDropdownOption(countrySelect, country);
    console.log(`Selected country: ${country}`);

    // Wait for form to be ready
    await new Promise(resolve => setTimeout(resolve, 500));

    // Step 4: Click the submit button
    const button = Array.from(document.querySelectorAll('button')).find(b =>
      b.textContent.includes('Get processing time')
    );

    if (!button) {
      throw new Error('Submit button not found');
    }

    button.click();
    console.log('Clicked submit button');

    // Wait for results to load
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Step 5: Extract the processing time result
    // The result structure varies, so we need to look for the processing time text
    const resultElement = document.querySelector('[class*="result"]') ||
                         document.querySelector('[id*="result"]') ||
                         document.body;

    return {
      category: category,
      applicationType: applicationType,
      country: country,
      processingTime: 'Result extraction needs to be implemented based on actual HTML structure',
      timestamp: new Date().toISOString(),
      rawHTML: resultElement ? resultElement.innerHTML : 'Not found'
    };

  } catch (error) {
    console.error('Error getting processing time:', error);
    return {
      category: category,
      applicationType: applicationType,
      country: country,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * Get all select options from a dropdown
 */
function getAllSelectOptions(selectElement) {
  return Array.from(selectElement.options)
    .filter(opt => opt.value !== '' && opt.value !== 'Make your selection...')
    .map(opt => ({
      value: opt.value,
      text: opt.text
    }));
}

/**
 * Export data structure
 */
function exportStructure() {
  const selects = document.querySelectorAll('select');
  const structure = {
    url: window.location.href,
    timestamp: new Date().toISOString(),
    selects: Array.from(selects).map((select, idx) => ({
      index: idx,
      id: select.id,
      name: select.name,
      optionsCount: select.options.length,
      options: getAllSelectOptions(select)
    }))
  };

  return structure;
}

// Export functions for use in Chrome DevTools
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CATEGORIES,
    TEMP_RESIDENCE_TYPES,
    getProcessingTime,
    getAllSelectOptions,
    exportStructure,
    selectDropdownOption,
    waitForElement
  };
}

console.log('Canada Processing Times Scraper loaded');
console.log('Available functions: getProcessingTime, exportStructure, getAllSelectOptions');
