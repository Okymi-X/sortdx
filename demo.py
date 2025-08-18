"""
Demonstration minimale de sortx fonctionnant sans dépendances externes.
"""

# Version simplifiée pour démonstration sans dépendances
def demo_basic_sorting():
    """Démonstration du tri de base."""
    print("=== DEMONSTRATION SORTX ===")
    print("Tri en mémoire de données structurées:\n")
    
    # Données test
    data = [
        {"nom": "Charlie", "age": 35, "salaire": 90000},
        {"nom": "Alice", "age": 25, "salaire": 85000},
        {"nom": "Bob", "age": 30, "salaire": 70000},
    ]
    
    print("Données originales:")
    for item in data:
        print(f"  {item}")
    
    # Tri par âge (simulation de sortx.sort_iter avec key("age", "num"))
    sorted_by_age = sorted(data, key=lambda x: x["age"])
    print(f"\nTrié par âge (équivalent: sortx.sort_iter(data, keys=[sortx.key('age', 'num')])):")
    for item in sorted_by_age:
        print(f"  {item}")
    
    # Tri par salaire descendant
    sorted_by_salary = sorted(data, key=lambda x: x["salaire"], reverse=True)
    print(f"\nTrié par salaire descendant (équivalent: sortx.sort_iter(data, keys=[sortx.key('salaire', 'num', desc=True)])):")
    for item in sorted_by_salary:
        print(f"  {item}")
    
    # Démonstration de tri multi-clés
    extended_data = [
        {"dept": "Engineering", "nom": "Charlie", "salaire": 90000},
        {"dept": "Engineering", "nom": "Alice", "salaire": 85000},
        {"dept": "Sales", "nom": "Bob", "salaire": 70000},
        {"dept": "Sales", "nom": "David", "salaire": 75000},
    ]
    
    print(f"\nDonnées avec départements:")
    for item in extended_data:
        print(f"  {item}")
    
    # Tri par département puis salaire descendant
    multi_key_sorted = sorted(extended_data, key=lambda x: (x["dept"], -x["salaire"]))
    print(f"\nTrié par département puis salaire desc (équivalent: sortx multi-key):")
    for item in multi_key_sorted:
        print(f"  {item}")


def demo_cli_features():
    """Démonstration des fonctionnalités CLI."""
    print(f"\n=== FONCTIONNALITES CLI SORTX ===")
    print("Commandes disponibles une fois installé:\n")
    
    cli_examples = [
        ("Tri CSV par prix numérique", 
         "sortx data.csv -o sorted.csv -k price:num"),
        
        ("Tri multi-clés avec locale française", 
         "sortx customers.csv -o sorted.csv -k country:str:locale=fr -k name:str"),
        
        ("Tri de gros fichier JSONL avec limite mémoire", 
         "sortx logs.jsonl.gz -o sorted.jsonl.gz -k timestamp:date --memory-limit=1G"),
        
        ("Tri naturel de noms de fichiers", 
         "sortx filenames.txt -o sorted.txt --natural"),
        
        ("Tri avec contrainte d'unicité", 
         "sortx users.jsonl -o unique.jsonl -k created_at:date --unique=user_id"),
        
        ("Afficher l'aide et exemples",
         "sortx --help\nsortx examples\nsortx types"),
    ]
    
    for i, (description, command) in enumerate(cli_examples, 1):
        print(f"{i}. {description}:")
        print(f"   {command}\n")


def demo_file_formats():
    """Démonstration des formats supportés."""
    print("=== FORMATS DE FICHIERS SUPPORTES ===")
    
    formats = [
        ("CSV/TSV", "Détection automatique des délimiteurs", "data.csv, data.tsv"),
        ("JSONL", "Un objet JSON par ligne", "logs.jsonl, events.ndjson"),
        ("TXT", "Texte brut, tri ligne par ligne", "filenames.txt"),
        ("Compressés", "Support gzip natif, zstd optionnel", "data.csv.gz, logs.jsonl.zst"),
    ]
    
    for format_name, description, examples in formats:
        print(f"• {format_name}: {description}")
        print(f"  Exemples: {examples}\n")


def demo_data_types():
    """Démonstration des types de données."""
    print("=== TYPES DE DONNEES SUPPORTES ===")
    
    types = [
        ("str", "Tri de chaînes avec support locale", "nom:str, category:str:locale=fr"),
        ("num", "Tri numérique (entiers/flottants)", "price:num, age:num"),
        ("date", "Tri de dates (ISO 8601, formats courants)", "created_at:date, timestamp:date"),
        ("nat", "Tri naturel (file2 < file10)", "filename:nat, version:nat"),
    ]
    
    for type_name, description, examples in types:
        print(f"• {type_name}: {description}")
        print(f"  Exemples: {examples}\n")


if __name__ == "__main__":
    try:
        demo_basic_sorting()
        demo_cli_features()
        demo_file_formats()
        demo_data_types()
        
        print("=" * 60)
        print("🎉 DEMONSTRATION SORTX COMPLETE!")
        print("=" * 60)
        print("\n📦 Pour installer:")
        print("pip install -e .")
        print("\n📖 Pour voir la documentation complète:")
        print("cat README.md")
        print("\n🧪 Pour lancer les tests:")
        print("pytest tests/")
        
    except Exception as e:
        print(f"Erreur dans la démonstration: {e}")
        import traceback
        traceback.print_exc()
