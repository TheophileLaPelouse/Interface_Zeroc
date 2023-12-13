document.addEventListener("DOMContentLoaded", function() {
    const fileInput = document.getElementById("uploadExcel");
    const uploadButton = document.getElementById("uploadButton");

    uploadButton.addEventListener("click", function() {
        const selectedFile = fileInput.files[0];

        if (selectedFile) {
            const formData = new FormData();
            formData.append("file", selectedFile);

            // Remplacer l'url par l'URL du futur serveur
            const serverURL = "votre_url_du_serveur";

            fetch(serverURL, {
                method: "POST",
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                console.log("Fichier envoyé avec succès.", data);
                alert("Fichier envoyé avec succès.");
            })
            .catch(error => {
                console.error("Erreur lors de l'envoi du fichier.", error);
                alert("Erreur lors de l'envoi du fichier.");
            });
        } else {
            alert("Veuillez sélectionner un fichier à envoyer.");
        }
    });
});