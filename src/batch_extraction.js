// Code slightly modified from the WebPlotDigitizer repository (node_examples/batch_process.js)

const jimp = require("jimp");
// Change according to your path
const wpd = require("../WebPlotDigitizer-4.6-win32-x64/WebPlotDigitizer-4.6-win32-x64/resources/app/wpd_node.js").wpd;
const fs = require("fs");
const path = require("path");
const sqlite3 = require('sqlite3').verbose();

// ---------- Parameters -----------------------

// Set defaults if parameters are not passed but default to using parameters
// for batch scripting using this process
const imagesPath = getArgvValue(process.argv, "--image-path=") || "../IR_spectral_data/mod_img_data";
const outputImagePath = getArgvValue(process.argv, "--output-path=") || "../IR_spectral_data/csv_data";
const outputJSONPath = getArgvValue(process.argv, "--output-json-path=") || "../IR_spectral_data/json_data";
const referenceProjectJSON = getArgvValue(process.argv, "--json-reference-file=") || "../IR_spectral_data/reference_project.json";
const dbPath = getArgvValue(process.argv,  "--database-path=") || "../IR_spectral_data/spectral_database.db";

const fileExtension = ".png";
// ---------------------------------------------

function getArgvValue(args, arg) {
    for (i = 0; i < args.length; i++) {
        if (args[i].startsWith(arg) === true) {
            var return_string = String(args[i].split("=")[1]);
        };
    };
    return return_string;
};

function createDatabase(dbPath) {
    // If the database file does not exist, create a new one
    return new sqlite3.Database(dbPath, (err) => {
        if (err) {
        console.error('Error opening database:', err.message);
        } else {
        console.log('Connected to the database');
        }
    });
  }

// Function to create a table in the database
function createTable(db, tableName) {
    const createTableQuery = `CREATE TABLE IF NOT EXISTS ${tableName} (x REAL, y REAL)`;
  
    db.run(createTableQuery, (err) => {
      if (err) {
        console.error(`Error creating table ${tableName}:`, err.message);
      } else {
        console.log(`Table ${tableName} created or already exists`);
      }
    });
  }

// Function to insert data into the table
function insertData(db, tableName, data) {
    const insertDataQuery = `INSERT INTO ${tableName} (x, y) VALUES (?, ?)`;
    db.run(insertDataQuery, [data[0], data[1]], (err) => {
      if (err) {
        console.error(`Error inserting data into ${tableName}:`, err.message);
      } else {
        console.log(`Data inserted into ${tableName}`);
      }
    });
  }

function digitizeImage(file, img, db) {
    //console.log("Reading: " + file);

    // load base project
    let plotData = new wpd.PlotData();
    let serializedPlotData = JSON.parse(fs.readFileSync(referenceProjectJSON, 'utf8'));
    plotData.deserialize(serializedPlotData);
    
    // clear existing datasets and re-run auto-extraction
    for (let ds of plotData.getDatasets()) {
        ds.clearAll();
        let autoDetector = plotData.getAutoDetectionDataForDataset(ds);
        if (autoDetector == null) {
            console.err("missing autodetector for: " + ds.name);
            continue;
        }
        let axes = plotData.getAxesForDataset(ds);
        autoDetector.imageWidth = img.bitmap.width;
        autoDetector.imageHeight = img.bitmap.height;
        autoDetector.generateBinaryData(img.bitmap);
        autoDetector.algorithm.run(autoDetector, ds, axes);
        
        // export CSV
        let csv = "x;y\n";
        for(let ptIdx = 0; ptIdx < ds.getCount(); ptIdx++) {
            let pt = ds.getPixel(ptIdx);
            let data = axes.pixelToData(pt.x, pt.y);
            insertData(db, path.basename(file, fileExtension), data)
            csv += data[0] + ";" + data[1] + "\n";
        }

        csvfilename = path.join(outputImagePath, path.basename(file, fileExtension) + ".csv");
        fs.writeFileSync(csvfilename, csv);
    }

    // export JSON specific to this image for later use
    let newSerializedPlotData = JSON.stringify(plotData.serialize());
    fs.writeFileSync(path.join(outputJSONPath, path.basename(file, fileExtension) + "_project.json"), newSerializedPlotData);
}

function doAllImages() {
    const db = createDatabase(dbPath);
    // Loop over all files in directory
    fs.readdir(imagesPath, function (err, files) {
        if (err) {
            return console.log('Unable to scan directory: ' + err);
        } 
        
        // loop over all files
        files.forEach(function (file) {
            createTable(db, path.basename(file, fileExtension))
            if (path.extname(file) == fileExtension) {
                // read image
                jimp.read(path.join(imagesPath, file)).then(img => {digitizeImage(file, img, db)});
            }
        });
    });
}

// read base project, then digitize all images in imagesPath
doAllImages();
console.log("Extraction done!")