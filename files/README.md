# Tutorial

The tutorial will be updated.

## Setup

### pytesseract (OCR)

To utilize the SDBSDataExtractor, it is essential to access both the [tesseract download tutorial](https://tesseract-ocr.github.io/tessdoc/Installation.html) and the [pytesseract usage tutorial](https://github.com/madmaze/pytesseract?tab=readme-ov-file). Skipping on using the class renders the engine download and package usage unnecessary.

### WebPlotDigitizer

To setup and execute the `*.js` file, is required to access the [WebPlotDigitizer tutorial](https://github.com/ankitrohatgi/WebPlotDigitizer/blob/master/node_examples/README.md).

## SDBSDataExtractor

If you possess the SDBS numbers for the compounds of interest, utilizing this function may be unnecessary. You have the option to directly modify an existing [CSV file](/IR_spectral_data/comp_sdbs_no.csv) or create a new one with the same name.

Upon executing this class, a message will be displayed in the console indicating that the system is now awaiting mouse clicks. Please follow the mouse click procedure as illustrated in the gif provided below.

![Clicking example](/tutorial_files/click_part.gif)

Following this, you'll need to verify the validity of the mouse clicks via the console:

    Retry the clicks? (y/n)

To ensure the clicks were accurately placed, you can inspect the [temporary files folder](/temp_files/), which should contain two images: one displaying the SDBS numbers and the other showing the compound names.

The numbers and names will be sequentially saved to the existing [CSV file](/IR_spectral_data/comp_sdbs_no.csv). To conclude the data extraction process, provide confirmation through the console:

    Continue capturing? (y/n)

Each iteration of the extracted data will have been securely saved.

## scrape_test.py

## modify_spectra_v2.py

## batch_test.js