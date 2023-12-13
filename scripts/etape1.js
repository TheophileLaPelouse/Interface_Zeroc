$(document).ready(function() {
    // Initialisation de la zone de glisser-déposer
    var uploadArea = document.querySelector(".upload-area");
    uploadArea.addEventListener("dragover", function(event) {
      event.preventDefault();
      uploadArea.classList.add("dragover");
    });
    uploadArea.addEventListener("dragleave", function(event) {
      event.preventDefault();
      uploadArea.classList.remove("dragover");
    });
    uploadArea.addEventListener("drop", function(event) {
      event.preventDefault();

      // Récupération du fichier déposé
      var file = event.dataTransfer.files[0];

      // Vérification de l'extension du fichier
      var extension = fileExtension(file);
      if (extension !== "ifc") {
          // Le fichier n'est pas de type IFC
          alert("Le fichier doit être de type IFC.");
          return;
      }

      // Affichage du nom du fichier
      var fileName = file.name;
      var uploadContainer = document.querySelector(".upload-container");
      uploadContainer.querySelector(".upload-button").innerHTML = fileName;

      // Affichage de l'aperçu du fichier
      var filePreview = base64_encode(file_get_contents(file.tmp_name));
      uploadContainer.querySelector(".upload-area").innerHTML = filePreview;

      // Empêcher le téléchargement du fichier
      event.preventDefault();

      // Empêcher l'ouverture d'une nouvelle page
      window.open = function() {};

      // Envoi du fichier au serveur Apache
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/upload", true);
      xhr.setRequestHeader("Content-Type", "multipart/form-data");
      xhr.onload = function() {
        if (xhr.status === 200) {
          // Le fichier est bien téléchargé
          // Stockage du fichier dans le répertoire "fichier téléchargé"
          var fileName = xhr.responseText;
          var destination = "/fichier téléchargé/" + fileName;
          var fileSaver = new FileSaver();
          fileSaver.save(file, destination);
        } else {
          // Une erreur s'est produite
        }
      };
      xhr.send(new FormData(document.getElementById("input-file")));

      // Vérification du téléchargement du fichier de manière temporaire
      var fileSaver = new FileSaver();
      var fileName = file.name;
      var file = document.getElementById("input-file").files[0];
      if (fileSaver.fileExists(fileName)) {
        // Le fichier existe déjà
        document.querySelector(".upload-button").innerHTML = "Fichier déjà existant";
    } else {
      // Le fichier n'existe pas
      document.querySelector(".upload-button").innerHTML = fileName;
    }
    });
  });