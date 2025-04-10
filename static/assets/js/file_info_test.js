/**
 * File Information Test Script
 *
 * This script tests the file information functionality in the file manager.
 * It verifies that file descriptions and favorite status are properly saved and displayed.
 *
 * Usage:
 * 1. Open the browser console in the file manager page
 * 2. Copy and paste this script into the console
 * 3. Run the script by calling runTest()
 */

function runTest() {
  console.log('Starting file information test...');

  // Find the first file info button
  const infoButton = document.querySelector('.btn-warning');
  if (!infoButton) {
    console.error('No file info button found');
    return;
  }

  // Get the file path
  const filePath = infoButton.getAttribute('data-file-path');
  if (!filePath) {
    console.error('No file path found on the info button');
    return;
  }

  console.log('Testing file with path:', filePath);

  // Click the info button to open the modal
  console.log('Opening file info modal...');
  infoButton.click();

  // Wait for the modal to open
  setTimeout(() => {
    // Get the form elements
    const form = document.getElementById('file-info-form');
    const descriptionField = document.getElementById('file-info');
    const favoriteCheckbox = document.getElementById('is-favorite');

    if (!form || !descriptionField || !favoriteCheckbox) {
      console.error('Form elements not found');
      return;
    }

    // Record the initial values
    const initialDescription = descriptionField.value;
    const initialFavorite = favoriteCheckbox.checked;

    console.log('Initial values:', {
      description: initialDescription,
      favorite: initialFavorite
    });

    // Set new values
    const newDescription = 'Test description ' + new Date().toISOString();
    const newFavorite = !initialFavorite;

    descriptionField.value = newDescription;
    favoriteCheckbox.checked = newFavorite;

    console.log('Set new values:', {
      description: newDescription,
      favorite: newFavorite
    });

    // Store the test values in localStorage for verification after reload
    const fileInfo = {
      path: filePath,
      info: newDescription,
      is_favorite: newFavorite,
      timestamp: Date.now()
    };

    // Also store the raw file path for debugging
    fileInfo.rawPath = filePath;
    fileInfo.encodedPath = encodeURIComponent(filePath);

    console.log('File info to be saved:', fileInfo);
    localStorage.setItem('savedFileInfo', JSON.stringify(fileInfo));
    console.log('Test values stored in localStorage for verification after reload');

    // Make sure the file path input is set correctly
    const filePathInput = document.getElementById('file-path-input');
    if (filePathInput) {
      filePathInput.value = filePath;
      console.log('Set file path input to:', filePath);
    } else {
      console.error('File path input not found');
    }

    // Submit the form
    console.log('Submitting form...');

    // Get the submit button
    const submitButton = form.querySelector('button[type="submit"]');
    if (!submitButton) {
      console.error('Submit button not found');
      return;
    }

    // Click the submit button
    submitButton.click();

    console.log('Form submitted. The page will reload and verification will run automatically.');
  }, 500);
}

// This function is no longer needed as we're using the verifyFileInfo function in the main page
function checkTestResult() {
  // The verification is now handled by the verifyFileInfo function in the main page
  // We'll keep this function for backward compatibility
  return;
}

// Run the check on page load
checkTestResult();

// Export the test function to the global scope
window.runTest = runTest;

console.log('File information test script loaded. Run the test by calling runTest() in the console.');
