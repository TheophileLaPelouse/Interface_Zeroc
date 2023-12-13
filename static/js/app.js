const express = require('express');
const { exec } = require('child_process');
const path = require('path');

const app = express();
const port = 5050;

// Serve HTML file from the 'html_files' directory
const htmlFilePath = path.join(__dirname, '../templates/simu.html');
app.get('/', (req, res) => {
    res.sendFile(htmlFilePath);
});

app.get('/run-python-script', (req, res) => {
    exec(`python3 ex.py`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return res.status(500).send('Internal Server Error');
        }
        const result = JSON.parse(stdout);
        console.log('Python script output:', result);
        res.json(result);
    });
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});

