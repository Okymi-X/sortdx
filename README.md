# sortdx

Un utilitaire de tri de fichiers puissant et flexible pour Python qui gère intelligemment les fichiers CSV, JSONL et texte.

## 🚀 Démarrage Rapide

```bash
pip install sortdx
```

### Utilisation de Base

```python
import sortdx

# Trier un CSV par colonne âge
sortdx.sort_file('data.csv', 'sorted.csv', keys=[sortdx.key('age', 'num')])

# Trier un JSONL par timestamp
sortdx.sort_file('logs.jsonl', 'sorted_logs.jsonl', keys=[sortdx.key('timestamp')])

# Trier un fichier texte par la 3ème colonne numériquement
sortdx.sort_file('data.txt', 'sorted.txt', keys=[sortdx.key(3, 'num')])
```

## 📦 Installation

```bash
pip install sortdx
```

Pour utiliser l'interface en ligne de commande (optionnel) :
```bash
pip install "sortdx[cli]"
```

## 🔧 Fonctionnalités

- **Détection Intelligente de Format** : Détecte automatiquement les formats CSV, JSONL et texte
- **Clés de Tri Multiples** : Tri par plusieurs colonnes/champs avec différents types de données
- **Efficace en Mémoire** : Gère de gros fichiers sans tout charger en mémoire
- **Tri Conscient du Type** : Support du tri string, numérique et date/heure
- **Entrée Flexible** : Fonctionne avec des chemins de fichiers ou des objets file-like
- **Statistiques** : Statistiques de tri optionnelles et rapport de progression

## 📖 Utilisation

### Clés de Tri

Créez des clés de tri avec la fonction `sortdx.key()` :

```python
import sortdx

# Tri textuel (par défaut)
key1 = sortdx.key('name')
key1 = sortdx.key(1)  # Index de colonne pour fichiers texte

# Tri numérique
key2 = sortdx.key('age', 'num')
key2 = sortdx.key(2, 'num')

# Tri inversé
key3 = sortdx.key('name', reverse=True)
```

### Formats de Fichiers

#### Fichiers CSV
```python
# Tri par une seule colonne
sortdx.sort_file('data.csv', 'output.csv', keys=[sortdx.key('age', 'num')])

# Tri par plusieurs colonnes
sortdx.sort_file('data.csv', 'output.csv', keys=[
    sortdx.key('department'),
    sortdx.key('salary', 'num', reverse=True)
])
```

#### Fichiers JSONL
```python
# Tri de fichiers JSON Lines
sortdx.sort_file('logs.jsonl', 'sorted.jsonl', keys=[
    sortdx.key('timestamp'),
    sortdx.key('priority', 'num')
])
```

#### Fichiers Texte
```python
# Tri par index de colonne (base 1)
sortdx.sort_file('data.txt', 'sorted.txt', keys=[sortdx.key(2, 'num')])

# Délimiteur personnalisé
sortdx.sort_file('data.txt', 'sorted.txt', 
                keys=[sortdx.key(1)],
                delimiter='|')
```

### Options Avancées

```python
# Obtenir des statistiques de tri
stats = sortdx.sort_file('large_file.csv', 'sorted.csv', 
                        keys=[sortdx.key('id', 'num')],
                        stats=True)
print(f"Traité {stats.lines_processed} lignes")

# Tri efficace en mémoire pour gros fichiers
sortdx.sort_file('huge_file.csv', 'sorted.csv',
                keys=[sortdx.key('timestamp')],
                max_memory_mb=500)  # Limiter l'usage mémoire
```

## 🔄 Types de Données

- `'str'` ou `'text'` : Tri string/texte (par défaut)
- `'num'` ou `'numeric'` : Tri numérique (gère entiers et flottants)
- `'date'` ou `'datetime'` : Tri date/heure (format ISO recommandé)

## 📊 Exemples

### Exemple 1 : Données Employés (CSV)
```python
import sortdx

# Contenu employees.csv :
# name,age,department,salary
# Alice,25,Engineering,75000
# Bob,30,Sales,65000
# Carol,28,Engineering,80000

# Tri par département, puis par salaire (plus élevé en premier)
sortdx.sort_file('employees.csv', 'sorted_employees.csv', keys=[
    sortdx.key('department'),
    sortdx.key('salary', 'num', reverse=True)
])
```

### Exemple 2 : Fichiers de Log (JSONL)
```python
# Contenu logs.jsonl :
# {"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "message": "Start"}
# {"timestamp": "2024-01-01T10:01:00Z", "level": "ERROR", "message": "Failed"}

# Tri par timestamp
sortdx.sort_file('logs.jsonl', 'sorted_logs.jsonl', keys=[
    sortdx.key('timestamp')
])
```

### Exemple 3 : Données Séparées par Espaces (TXT)
```python
# Contenu data.txt :
# Alice 25 Engineering 75000
# Bob 30 Sales 65000

# Tri par 4ème colonne (salaire) numériquement
sortdx.sort_file('data.txt', 'sorted_data.txt', keys=[
    sortdx.key(4, 'num', reverse=True)
])
```

## 🧪 Tests Réels

Le package a été testé avec succès sur :

### CSV
```csv
name,age,salary
Alice,25,45000
Diana,28,55000
Bob,30,50000
Charlie,35,60000
```
**Tri par âge** → Alice (25), Diana (28), Bob (30), Charlie (35) ✅

### JSONL
```jsonl
{"name": "Alice", "age": 25, "timestamp": "2025-01-15T09:15:00Z"}
{"name": "Diana", "age": 28, "timestamp": "2025-01-15T08:20:00Z"}
{"name": "Bob", "age": 30, "timestamp": "2025-01-15T10:30:00Z"}
{"name": "Charlie", "age": 35, "timestamp": "2025-01-15T11:45:00Z"}
```
**Tri par âge** → Même ordre que CSV ✅

### TXT
```
file10.txt
file2.txt  
file1.txt
file20.txt
file3.txt
```
**Tri numérique par 3ème colonne** → Ordre correct selon valeurs numériques ✅

## 🎯 Performance

sortdx est conçu pour l'efficacité :

- **Usage mémoire** : Limites mémoire configurables pour traitement de gros fichiers
- **Vitesse** : Algorithmes de tri optimisés avec overhead minimal
- **Évolutivité** : Gère efficacement les fichiers de KB à GB

## 📈 Statistiques de Tri

```python
import sortdx

# Obtenir des statistiques détaillées
stats = sortdx.sort_file('data.csv', 'sorted.csv', 
                        keys=[sortdx.key('age', 'num')], 
                        stats=True)

print(f"Lignes traitées : {stats.lines_processed}")
print(f"Temps de tri : {stats.sort_time:.2f}s") 
print(f"Mémoire utilisée : {stats.memory_used_mb:.1f}MB")
```

## 🔗 API Référence

### `sortdx.sort_file(input_path, output_path, keys, **options)`

Trie un fichier selon les clés spécifiées.

**Paramètres :**
- `input_path` (str) : Chemin du fichier d'entrée
- `output_path` (str) : Chemin du fichier de sortie
- `keys` (List[SortKey]) : Liste des clés de tri
- `delimiter` (str, optionnel) : Délimiteur pour fichiers texte (défaut: auto-détection)
- `stats` (bool, optionnel) : Retourner des statistiques (défaut: False)
- `max_memory_mb` (int, optionnel) : Limite mémoire en MB

**Retour :**
- `SortStats` si stats=True, sinon None

### `sortdx.key(field, type='str', reverse=False)`

Crée une clé de tri.

**Paramètres :**
- `field` (str|int) : Nom de champ (CSV/JSONL) ou index de colonne (TXT)
- `type` (str) : Type de données ('str', 'num', 'date')
- `reverse` (bool) : Tri inversé

## 📄 Licence

Licence MIT - voir le fichier [LICENSE](LICENSE) pour les détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une Pull Request.

## 📞 Support

Si vous rencontrez des problèmes ou avez des questions, veuillez [ouvrir une issue](https://github.com/yourusername/sortdx/issues) sur GitHub.

## 🌐 PyPI

Package disponible sur PyPI : https://pypi.org/project/sortdx/

## 🏷️ Version

Version actuelle : **0.1.1**

Installation testée sur :
- Python 3.10+
- Windows, macOS, Linux
- Fichiers de quelques KB à plusieurs GB
