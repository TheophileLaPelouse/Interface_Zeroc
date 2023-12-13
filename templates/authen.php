<?php
// Configuration de la base de données
$servername = "localhost";
$username = "hippolyte";
$password = "votre_mot_de_passe";
$dbname = "votre_base_de_donnees";

// Création de la connexion à la base de données
$conn = new mysqli($servername, $username, $password, $dbname);

// Vérification de la connexion
if ($conn->connect_error) {
    die("La connexion à la base de données a échoué : " . $conn->connect_error);
}

// Traitement du formulaire d'authentification
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Récupération des données du formulaire
    $username = $_POST["username"];
    $password = $_POST["password"];

    // Requête SQL sécurisée
    $stmt = $conn->prepare("SELECT * FROM utilisateurs WHERE nom_utilisateur = ? AND mot_de_passe = ?");
    $stmt->bind_param("ss", $username, $password);

    // Exécution de la requête
    $stmt->execute();

    // Vérification des résultats
    $result = $stmt->get_result();

    if ($result->num_rows == 1) {
        // L'utilisateur est authentifié avec succès
        echo "Authentification réussie!";
    } else {
        // L'authentification a échoué
        echo "Nom d'utilisateur ou mot de passe incorrect!";
    }

    // Fermeture de la requête
    $stmt->close();
}

// Fermeture de la connexion à la base de données
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page d'authentification</title>
</head>
<body>
    <h2>Authentification</h2>
    <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
        <label for="username">Nom d'utilisateur:</label>
        <input type="text" name="username" required><br>

        <label for="password">Mot de passe:</label>
        <input type="password" name="password" required><br>

        <input type="submit" value="Se connecter">
    </form>
</body>
</html>