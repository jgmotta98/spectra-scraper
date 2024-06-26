# Spectra Scraper

Easy to use scraper to batch download infrared spectra from the free website Spectral Database for Organic Compounds (SDBS), extract and store its numerical data into a database (`.db` file from sqlite3) for data analysis.

## How to use

You can access the tutorial [here](./src/README.md) and follow the step by step guide.

The purpose of the spectra scraper is to return a complete `spectral_database.db` file at the end to be use for any spectral related machine learning training or batch data analysis.

## Credits

- Numerical data extraction made with standard [WebPlotDigitizer](https://github.com/ankitrohatgi/WebPlotDigitizer/tree/master).
- Data extracted from the [Spectral Database for Organic Compounds (SDBS)](https://sdbs.db.aist.go.jp/sdbs/cgi-bin/cre_index.cgi).
- Baseline correction (Whittaker smoothing & airPLS) from [Z.-M. Zhang, S. Chen, and Y.-Z. Liang, 2010](https://doi.org/10.1039/B922045C).

## License

[MIT](./LICENSE) © Spectra Scraper
