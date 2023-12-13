document.addEventListener('DOMContentLoaded', function () {
    const apiKey = '79e6fc8cc55049359f89f370e77484d4';
    const searchButton = document.getElementById('search-button');
    const zipcodeInput = document.getElementById('zipcode');
    const resultZip = document.getElementById('result-zip');
    const resultCity = document.getElementById('result-city');

    searchButton.addEventListener('click', () => {
        const zip = zipcodeInput.value;
        if (zip) {
            fetch(`https://api.opencagedata.com/geocode/v1/json?q=${zip}&key=${apiKey}&countrycode=FR&language=fr&pretty=1`)
                .then(response => response.json())
                .then(data => {
                    const firstResult = data.results[0];
                    if (firstResult) {
                        resultZip.textContent = firstResult.components.postcode;
                        resultCity.textContent = firstResult.components.city || 'Ville inconnue';
                    } else {
                        resultZip.textContent = 'Code postal inconnu';
                        resultCity.textContent = '';
                    }
                })
                .catch(error => {
                    console.error(error);
                    resultZip.textContent = 'Erreur de recherche';
                    resultCity.textContent = '';
                });
        }
    });
});
