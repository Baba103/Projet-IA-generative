# 🦒 Guide d'Utilisation de Git LFS (Large File Storage)

Ce projet utilise **Git LFS** pour gérer les fichiers volumineux (archives .zip, modèles, bases de données). Voici comment l'utiliser correctement.

---

## 1. Installation de Git LFS

Avant de cloner ou d'interagir avec ce dépôt, vous devez installer l'extension Git LFS sur votre machine.

### Windows
Téléchargez et installez l'exécutable depuis [git-lfs.com](https://git-lfs.com).
Ou via Winget :
```bash
winget install GitHub.GitLFS
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install git-lfs
```

### MacOS
```bash
brew install git-lfs
```

---

## 2. Initialisation (Une seule fois)

Une fois installé, activez LFS dans votre configuration globale Git :

```bash
git lfs install
```
*Vous devriez voir : `Git LFS initialized.`*

---

## 3. Cloner le Projet

Lorsque vous clonez le dépôt, Git LFS téléchargera automatiquement les fichiers volumineux.

```bash
git clone https://github.com/Baba103/Projet-IA-generative.git
```

Si vous avez déjà cloné le projet sans LFS, récupérez les gros fichiers avec :
```bash
git lfs pull
```

---

## 4. Ajouter de nouveaux fichiers volumineux

Si vous devez ajouter un nouveau fichier de plus de 100 Mo (ex: `nouveau_dataset.zip`) :

1.  **Dites à LFS de le suivre** (avant de l'ajouter !) :
    ```bash
    git lfs track "*.zip"
    ```
    *(Cela met à jour le fichier `.gitattributes`)*

2.  **Ajoutez vos fichiers normalement** :
    ```bash
    git add .gitattributes
    git add votre_fichier.zip
    git commit -m "Ajout dataset"
    git push origin main
    ```

---

## ⚠️ Résolution des Erreurs Courantes

### "This is larger than GitHub's recommended maximum file size"
Si vous voyez cette erreur lors d'un push, c'est que vous essayez de pousser un gros fichier **sans** qu'il soit traqué par LFS.

**Solution :**
1. Retirez le fichier de la zone de staging : `git reset HEAD~1` (si commité) ou `git restore --staged <fichier>`
2. Trackez-le : `git lfs track "*.ext"`
3. Réessayez.

### "Smudge error: ... HTTP 404"
Parfois dû à un dépassement de quota (bande passante) sur GitHub gratuit. Essayez de cloner uniquement la dernière version :
```bash
git clone --depth 1 https://github.com/Baba103/Projet-IA-generative.git
```
