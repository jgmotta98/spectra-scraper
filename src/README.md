# Tutorial

Updates beyond the control of this repository may lead to the tutorial becoming outdated or non-functional. After reading the tutorial, run `main.py`.

## Setup

### pytesseract (OCR)

To utilize the SDBSDataExtractor, it is essential to access both the [tesseract download tutorial](https://tesseract-ocr.github.io/tessdoc/Installation.html) and the [pytesseract usage tutorial](https://github.com/madmaze/pytesseract?tab=readme-ov-file). Skipping on using the class renders the engine download and package usage unnecessary.

### WebPlotDigitizer

To setup and execute the `*.js` file, is required to access the [WebPlotDigitizer tutorial](https://github.com/ankitrohatgi/WebPlotDigitizer/blob/master/node_examples/README.md).

## SDBSDataExtractor

If you possess the SDBS numbers for the compounds of interest, utilizing this function may be unnecessary. You have the option to directly modify an existing [CSV file](/IR_spectral_data/comp_sdbs_no.csv) or create a new one with the same name.

Upon executing this class, a message will be displayed in the console indicating that the system is now awaiting mouse clicks. Please follow the mouse click procedure as illustrated in the video provided below.

https://github.com/jgmotta98/spectra-scraper/assets/90492274/c1ed7ead-2603-4161-8d14-7250cd6adecc

Following this, you'll need to verify the validity of the mouse clicks via the console:

    Retry the clicks? (y/n)

To ensure the clicks were accurately placed, you can inspect the [temporary files folder](/temp_files/), which should contain two images: one displaying the SDBS numbers and the other showing the compound names.

The numbers and names will be sequentially saved to the existing [CSV file](/IR_spectral_data/comp_sdbs_no.csv). To conclude the number and names extraction process, provide confirmation through the console:

    Continue capturing? (y/n)

Each iteration of the extracted data will have been securely saved.

## SDBSPageScraper

This class will download the infrared (IR) spectra made in liquid film of the desired compounds.

Make sure that the compound has a valid IR spectra; in the absence of such data, no image will be downloaded.

You will have the choice to increase the number of chrome instances to download more images in a faster pace.

## SpectraMod

Following the download, the images will be formatted for compatibility with WebPlotDigitizer's code.

## batch_extraction.js

The [reference project](/IR_spectral_data/reference_project.json) enables batch extraction and can be tailored through the WebPlotDigitizer application. Adjustments can be made by saving a new `.json` file.

All data gathered during the process will be accessible in the [IR_spectral_data](/IR_spectral_data) folder.

In case of any of the images on the [img_data](/IR_spectral_data/img_data/) folder turn out like the one below, the task is to delete those images and then rerun the code.

![faild_forbidden](https://github.com/jgmotta98/spectra-scraper/assets/90492274/6cd60ace-a854-4464-aa99-18c8808ddba1)

## store_database.py

This function uses the Whittaker smoothing and the airPLS algorithm of baseline correction from [Z.-M. Zhang, S. Chen, and Y.-Z. Liang, 2010](https://doi.org/10.1039/B922045C) to correct the collected data. The data is stored in a sqlite3 `.db` file for future use.
