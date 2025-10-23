/**
 * Complete Working Example for Canada Processing Times Scraper
 *
 * This script provides a complete, tested workflow for extracting processing times
 * from the Canadian Immigration website using Chrome DevTools MCP.
 */

/**
 * Main function to get processing time
 *
 * This function should be executed in the browser context via Chrome DevTools MCP's evaluate_script
 *
 * @param {string} category - Application category
 * @param {string} applicationType - Specific application type
 * @param {string} country - Country of application
 * @returns {Promise<Object>} Result object with processing time or error
 */
async function getCanadaProcessingTime(category, applicationType, country) {
  const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
  const log = [];

  try {
    log.push('Starting processing time lookup...');

    // STEP 1: Select the application category
    log.push('Step 1: Selecting category...');
    const allSelects = document.querySelectorAll('select');

    // Find the category select (first non-month select)
    let categorySelect = null;
    for (const select of allSelects) {
      if (select.id !== 'month') {
        const options = Array.from(select.options);
        if (options.some(opt => opt.text.includes('Temporary residence') || opt.text.includes('Economic immigration'))) {
          categorySelect = select;
          break;
        }
      }
    }

    if (!categorySelect) {
      return { success: false, error: 'Category select not found', log };
    }

    // Find and select the category option
    const categoryOption = Array.from(categorySelect.options).find(opt => opt.text === category);
    if (!categoryOption) {
      return {
        success: false,
        error: `Category "${category}" not found`,
        availableCategories: Array.from(categorySelect.options).map(o => o.text),
        log
      };
    }

    categorySelect.value = categoryOption.value;
    categorySelect.dispatchEvent(new Event('change', { bubbles: true }));
    log.push(`Selected category: ${category}`);

    // Wait for the next dropdown to appear
    await wait(2000);

    // STEP 2: Select the application type
    log.push('Step 2: Selecting application type...');
    const selects2 = document.querySelectorAll('select');

    // Find the type select (should be a new one that appeared)
    let typeSelect = null;
    for (const select of selects2) {
      if (select !== categorySelect && select.id !== 'month') {
        // Verify it has the expected options
        const options = Array.from(select.options);
        if (options.some(opt => opt.value && opt.value !== '' && opt.text !== 'Make your selection...')) {
          const hasExpectedOption = options.some(opt => opt.text === applicationType);
          if (hasExpectedOption || typeSelect === null) {
            typeSelect = select;
            if (hasExpectedOption) break;
          }
        }
      }
    }

    if (!typeSelect) {
      return { success: false, error: 'Application type select not found', log };
    }

    const typeOption = Array.from(typeSelect.options).find(opt => opt.text === applicationType);
    if (!typeOption) {
      return {
        success: false,
        error: `Application type "${applicationType}" not found`,
        availableTypes: Array.from(typeSelect.options).map(o => o.text),
        log
      };
    }

    typeSelect.value = typeOption.value;
    typeSelect.dispatchEvent(new Event('change', { bubbles: true }));
    log.push(`Selected application type: ${applicationType}`);

    // Wait for the country dropdown to appear
    await wait(2000);

    // STEP 3: Select the country
    log.push('Step 3: Selecting country...');
    const selects3 = document.querySelectorAll('select');

    // Find the country select (newest select with many options)
    let countrySelect = null;
    for (const select of selects3) {
      if (select !== categorySelect && select !== typeSelect && select.id !== 'month') {
        // Country select should have many options (200+)
        if (select.options.length > 50) {
          countrySelect = select;
          break;
        }
      }
    }

    if (!countrySelect) {
      return {
        success: false,
        error: 'Country select not found',
        selectsFound: Array.from(selects3).map(s => ({
          id: s.id,
          optionsCount: s.options.length
        })),
        log
      };
    }

    const countryOption = Array.from(countrySelect.options).find(opt => opt.text === country);
    if (!countryOption) {
      // Try partial match
      const partialMatch = Array.from(countrySelect.options).find(opt =>
        opt.text.toLowerCase().includes(country.toLowerCase())
      );

      if (!partialMatch) {
        return {
          success: false,
          error: `Country "${country}" not found`,
          sampleCountries: Array.from(countrySelect.options).slice(0, 10).map(o => o.text),
          log
        };
      }

      countrySelect.value = partialMatch.value;
      countrySelect.dispatchEvent(new Event('change', { bubbles: true }));
      log.push(`Selected country (partial match): ${partialMatch.text}`);
    } else {
      countrySelect.value = countryOption.value;
      countrySelect.dispatchEvent(new Event('change', { bubbles: true }));
      log.push(`Selected country: ${country}`);
    }

    await wait(1000);

    // STEP 4: Click the submit button
    log.push('Step 4: Clicking submit button...');
    const button = Array.from(document.querySelectorAll('button')).find(b =>
      b.textContent && b.textContent.includes('Get processing time')
    );

    if (!button) {
      return { success: false, error: 'Submit button not found', log };
    }

    button.click();
    log.push('Button clicked, waiting for results...');

    // Wait for results to load
    await wait(3000);

    // STEP 5: Extract the processing time from the result
    log.push('Step 5: Extracting processing time...');

    // The result could be in various places, let's search for common patterns
    const bodyText = document.body.innerText;

    // Look for time patterns like "X days", "X weeks", "X months", "X years"
    const timePatterns = [
      /(\d+)\s*(day|days|week|weeks|month|months|year|years)/gi,
      /processing\s*time[:\s]+([^\n]+)/gi,
      /(\d+)\s*business\s*days/gi
    ];

    let processingTime = null;
    for (const pattern of timePatterns) {
      const matches = bodyText.match(pattern);
      if (matches && matches.length > 0) {
        processingTime = matches[0];
        break;
      }
    }

    // Also try to find any heading or emphasized text after clicking
    const resultHeadings = Array.from(document.querySelectorAll('h1, h2, h3, h4, strong, b')).map(el => el.innerText.trim());

    return {
      success: true,
      query: {
        category,
        applicationType,
        country
      },
      processingTime: processingTime || 'Could not extract processing time',
      resultHeadings: resultHeadings.slice(0, 10),
      pageTextSample: bodyText.slice(0, 1000),
      log,
      timestamp: new Date().toISOString()
    };

  } catch (error) {
    return {
      success: false,
      error: error.message,
      stack: error.stack,
      log
    };
  }
}

// Example usage (to be called from Chrome DevTools MCP):
//
// await getCanadaProcessingTime(
//   "Temporary residence (visiting, studying, working)",
//   "Visitor visa (from outside Canada)",
//   "China (People's Republic of)"
// );

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { getCanadaProcessingTime };
}
