window.runPythonScript = function() {
    fetch('/run-python-script')
        .then(response => response.json())
        .then(result => {
            // Update a div with the result
            document.getElementById('result-container').innerText = `Result: ${result.join(', ')}`;
        })
        .catch(error => {
            console.error('Error:', error);
            // Display an error message on the webpage
            alert('An error occurred while running the Python script.');
        });
};
