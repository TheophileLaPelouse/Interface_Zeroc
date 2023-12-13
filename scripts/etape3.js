
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
        // Envoi du fichier sur le serveur
        $.ajax({
          url: "/upload",
          type: "POST",
          data: {
            file: file
          }
        }).done(function(data) {
          // Affichage du nom et de l'aperçu du fichier
          var fileName = data.name;
          var filePreview = data.preview;
          var uploadContainer = document.querySelector(".upload-container");
          uploadContainer.querySelector(".upload-button").innerHTML = fileName;
          uploadContainer.querySelector(".upload-area").innerHTML = filePreview;
        });
      });
    });
  